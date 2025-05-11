import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// Custom metrics for recording task execution time
const TaskDurationTrend = new Trend('task_duration', true);
const WAVESPEED_API_KEY = __ENV.WAVESPEED_API_KEY;

export const options = {
  scenarios: {
    concurrent_5: {
      executor: 'constant-arrival-rate',
      timeUnit: '1m',
      duration: '150s',
      preAllocatedVUs: 2,
      rate: 5,
      maxVUs: 5,
    },
    concurrent_10: {
      executor: 'constant-arrival-rate',
      timeUnit: '1m',
      duration: '150s',
      preAllocatedVUs: 5,
      rate: 10,
      maxVUs: 10,
      startTime: '155s', // 5 seconds after 5 concurrent scenario
    },
  },
};

export default function () {
  // Submit task
  const submitUrl = "https://api.wavespeed.ai/api/v2/wavespeed-ai/wan-2.1/i2v-480p";
  const submitHeaders = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${WAVESPEED_API_KEY}`
  };
  const submitPayload = JSON.stringify({
    "duration": 10,
    "enable_safety_checker": true,
    "flow_shift": 3,
    "guidance_scale": 5,
    "image": "https://d2g64w682n9w0w.cloudfront.net/media/images/1745136833067505009_dqvqnjhd.jpg",
    "negative_prompt": "",
    "num_inference_steps": 30,
    "prompt": "A confident young tech professional standing in a modern office space, talking to the camera with calm gestures. Soft daylight, clean environment, business casual outfit, focused expression. Center frame, smooth motion",
    "seed": -1,
    "size": "832*480"
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
      taskId = body.data.id; // Adjust based on actual response structure
      return !!taskId;
    },
  });

  if (!taskId) {
    console.error('No taskId received, skipping polling');
    return;
  }

  // Poll task status
  const pollUrl = `https://api.wavespeed.ai/api/v2/predictions/${taskId}/result`; // Replace with actual status API
  const maxAttempts = 150; // Maximum polling attempts
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
    const status = pollBody.data.status; // Adjust based on actual response structure

    if (status === 'completed') {
      taskSuccessful = true;
      const duration = pollBody.data.executionTime;
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