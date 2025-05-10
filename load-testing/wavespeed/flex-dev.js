import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// Custom metrics for recording task execution time
const TaskDurationTrend = new Trend('task_duration', true);
const WAVESPEED_API_KEY = "";

export const options = {
  scenarios: {
    concurrent_10: {
      executor: 'constant-vus',
      vus: 10, // 10 concurrent users
      duration: '30s',
    },
    concurrent_20: {
      executor: 'constant-vus',
      vus: 30, // 30 concurrent users
      duration: '30s',
      startTime: '35s', // 5 seconds after 10 concurrent scenario
    },
  },
};

export default function () {
  // Submit task
  const submitUrl = "https://api.wavespeed.ai/api/v2/wavespeed-ai/flux-dev";
  const submitHeaders = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${WAVESPEED_API_KEY}`
  };
  const submitPayload = JSON.stringify({
    // Fill in payload according to actual API requirements
    "enable_base64_output": true,
    "enable_safety_checker": true,
    "guidance_scale": 3.5,
    "num_images": 1,
    "num_inference_steps": 28,
    "prompt": "A stylish model, fashion show, showcase a designer outfit, orange colour suit, conspicuous jewelry, fashion show background, vibrant color, dramatic makeup",
    "seed": -1,
    "size": "1024*1024",
    "strength": 0.8
  });

  const submitRes = http.post(submitUrl, submitPayload, {
    headers: submitHeaders,
  });

  // Check if submission was successful and get task ID
  let taskId;
  check(submitRes, {
    'submit is status 200': (r) => r.status === 200,
    'submit response has taskId': (r) => {
      const body = r.json();
      taskId = body.data.id; // Adjust according to actual response structure
      return !!taskId;
    },
  });

  if (!taskId) {
    console.error('No taskId received, skipping polling');
    return;
  }

  // Poll task status
  const pollUrl = `https://api.wavespeed.ai/api/v2/predictions/${taskId}/result`; // Replace with actual status API
  const maxAttempts = 30; // Maximum polling attempts
  const pollInterval = 1; // Polling interval (seconds)
  let attempts = 0;
  let taskSuccessful = false;

  while (attempts < maxAttempts) {
    const pollRes = http.get(pollUrl,{
        headers: submitHeaders,
    });

    check(pollRes, {
      'poll is status 200': (r) => r.status === 200,
    });

    const pollBody = pollRes.json();
    const status = pollBody.data.status; // Adjust according to actual response structure

    if (status === 'completed') {
      taskSuccessful = true;
      const duration = pollBody.data.executionTime / 1000;
      TaskDurationTrend.add(duration);
      break;
    } else if (status === 'failed') {
      console.warn(`Task ${taskId} failed`);
      break;
    }

    attempts++;
    sleep(pollInterval);
  }

  // Check if task was successful
  check(taskSuccessful, {
    'task completed successfully': (success) => success === true,
  });

  if (!taskSuccessful) {
    console.warn(`Task ${taskId} did not complete successfully after ${maxAttempts} attempts`);
  }
}