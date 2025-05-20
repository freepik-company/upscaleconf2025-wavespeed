import time
import json
import random
from locust import HttpUser, task, between

class CeleryTaskUser(HttpUser):
    """
    Locust user that continuously submits tasks to the Celery API
    """
    wait_time = between(1, 3)  # Wait between 1 and 3 seconds between tasks
    
    def on_start(self):
        """Initialize the user session"""
        self.client.headers = {'Content-Type': 'application/json'}
        self.prompts = [
            "surreal and dreamlike, saturated, pastel, dreamy atmosphere, liquid psychedelic, Expressionism focuses on emotional experience rather than physical reality. How do distorted figures and exaggerated colors in Expressionism convey intense feelings, and what does this say about the artist’s inner world?",
            "In a pastel-drenched dreamscape, faceless figures stretch and blur through melting architecture. Psychedelic hues and expressive brushstrokes capture the dissonance between memory and emotion in an abstract expressionist tone.",
            "An elegant Asian male model with a retro television head, walking through a vibrant, neon-lit Tokyo street during a light rain. He is dressed in a sleek, black trench coat with colorful, geometric patterns, blending minimal fashion with solar punk elements. The photograph, taken with an 85mm lens, highlights the realistic reflections and the futuristic yet retro vibe, present day.",
            "A futuristic fashion editorial featuring a model with a holographic helmet shaped like a CRT screen, striding through a post-cyberpunk alley under acid rain. The trench reflects shifting neon ads in vivid solar-punk style.",
            "an asian man face is centered and covered in real cutted white flowers, Zara shooting, petals fall in front of him, background is a cloudy sky, Yves Saint Laurent style, analog effect, cinematographic photograph, movement effect",
            "Portrait of a man emerging from a sea of wilted petals, sharp contrast between the organic decay and the glossy editorial lighting. Wind sweeps petals across a blurred analog lens for an emotional cinematic still.",
            "A single vibrant flower is frozen mid-bloom inside a block of translucent cracked ice, suspended against a soft muted blue background. Air bubbles and fractures magnify its textures. Captured with a nostalgic 35mm aesthetic, slightly overexposed in highlights. Frame the image with a black film border., The style is Scandinavian with diffused pale light for a soft, minimal look, gold glow bright orange color, professionally color graded visual",
            "Macro close-up of a dandelion seed frozen in crystalline amber, air bubbles and iridescence trapped inside. Diffused Scandinavian-style light reveals frost detail, with slight bloom and grain film effect.",
            "A crochet hood with intricate lace-like patterns, styled in deep black yarn, worn by a model with stark contour lighting that casts dramatic shadows across their face, set against a dark orange background.",
            "A dramatic close-up of a lace-stitched mask worn by a genderless figure, illuminated with directional tungsten light. Warm shadows cascade on textured fabric over a burnt sienna backdrop.",
            "A father and baby son sharing a heartfelt embrace, one with dark skin and the other with albinism. High contrast lighting with a minimalist background highlights the warmth and dignity of familial connection",
            "Intimate portrait of a man and a woman seated forehead to forehead, eyes closed. Harsh rim light separates skin tones in chiaroscuro against a smoky neutral backdrop. Stylized to evoke vulnerability and closeness.",
            "A surreal 3/4 mid-body portrait of a ghostly robot with translucent chest and head revealing a pulsing galaxy, draped in abundant futuristic fabrics resembling smoke flowing around the robots, filling the room, vibrant metallic tones with a nebula inside, ethereal lighting, white wasteland background, intricate details, hyper-realistic, 8K, ideal for striking contemporary gallery displays",
            "A transparent android torso revealing a miniature star system within. Cosmic fog flows from its limbs like silken ribbons in zero gravity. Displayed in an art gallery on a glowing plinth under spectral lighting.",
            "A 25-year-old Caucasian woman with a silver mask and a gray turban, in a dense foggy forest, wearing a dark cloak, mysterious atmosphere.",
            "A hooded woman with frost-covered lashes and silver jewelry stands amid ghostly trees. Morning fog swirls around her cloak as dawn breaks, casting cold lavender shadows across her face.",
            "An avant-garde fashion portrait in black and white featuring a model with pale skin and silver hair, their face partly framed by a black-painted hand emerging from above. The hand outlines the eye and mouth area, blending sculpture with emotion. Sharp lighting, bold contrast, symbolic of surveillance and identity.",
            "A grayscale fashion photo of a model's face obscured by fingers painted metallic black. Only one eye visible, catching a glint of light in an otherwise heavily contrasted frame, symbolism of fragmentation and gaze.",
            "Close-up of a pair of futuristic sandals with translucent straps and a glossy dark red chrome base. The reflective surfaces capture subtle highlights, creating depth and a surreal aesthetic against the minimalist background",
            "Stylized still of concept footwear floating mid-air in a white vacuum. Shoes cast twin soft shadows below; chrome soles glisten with gradient tones and ghostlike glows mimic product photography on LSD.",
            "Create a whimsical and surreal portrait of a romantic couple in 18th-century attire, standing in a pastoral landscape. Replace their heads with fast food items: the man has a cheeseburger for a head, and the woman has a container of French fries as a head. Maintain the classical painting style, with rich details, soft lighting, and a loyal dog by their side looking up at them. Blend the food heads naturally with the scene for a humorous yet elegant composition.",
            "Two baroque-era aristocrats recline on velvet chaise lounges, one with a donut crown and the other with a milkshake tiara. Flemish lighting and soft brushstroke textures elevate the absurd to regal surrealism.",
            "The style is dark and mysterious, inspired by neo-expressionism, A partially collapsed concrete sculpture resembling a woman's face, stands on a rocky shore. The sun is setting in the background, casting a warm glow through the statue's cracks. The ocean waves crash against the rocks, and the sky is filled with clouds, creating a dramatic atmosphere",
            "Broken marble faces with rusted edges rise from a storm-lashed beach. Their hollow eyes echo the erosion of memory. Light filters through storm clouds in a painterly palette of indigo, rust, and violet.",
            "una monja suspendida en el aire, fondo minimalista",
            "A levitating nun draped in matte black robes, floats against a pure ivory wall. Her form is still, hands in prayer, hem fluttering slightly — shot in shallow depth of field with film grain and holy silence.",
            "A highly detailed photograph of a person sitting, showcasing intricately designed prosthetic leg with an ornate, baroque aesthetic. The prosthetics feature gold filigree and pearls, pastel blue, with mechanical joints and decorative engravings. flat footwear is seamlessly integrated into the design, adorned with spikes and embellishments that add a regal, almost fantasy-like presence. One natural leg. The soft, diffused lighting highlights the luxurious textures and gold details, creating a striking contrast between the organic and mechanical elements. pastel soft yellow color background",
            "Baroque-inspired prosthetic arm extending toward soft light, made of glass tubes and gilded accents, adorned with pearl strings and ornate flourishes. Photographed on pale blush backdrop in a fine art editorial style.",
            "a black eagle, side profile. the eagle is wearing a pink diamond necklace. red background. analog, professional portrait photography shot",
            "A parrot encrusted in gold leaf sits in profile, wearing a feathered collar and emerald pendant. Crimson velour backdrop, deep vignette, and analog filter mimic a fashion lookbook for regal birds.",
            "black woman, extra long hair made of pearls",
            "Profile of a woman whose braided pearl hair wraps around her neck like a collar. Lit from behind with a soft rim light, her silhouette radiates quiet grace on a velvet teal background.",
            "a hand adorned with numerous colorful and eye-catching rings, each featuring unique designs, gemstones, and playful motifs. The rings vary in shapes, including hearts, stars, clovers, clouds, and geometric patterns, with vibrant colors such as pink, blue, gold, and iridescent hues. Many of the rings have large, glittering stones, opalescent surfaces, or pearl accents, giving a maximalist, whimsical aesthetic. The nails are painted in a glossy pink gradient with tiny glitter details, complementing the extravagant and playful jewelry. pastel yellow and pink background",
            "An overhead flat lay of hands cradling tiny toy planets, fingers wrapped in glittery surrealist rings. The nail polish shifts between holographic pink and chrome silver under pastel lighting.",
            "A striking digital illustration of a woman embodying Leo, glowing in golden, fiery hues. She wears a futuristic, regal armor with metallic textures, resembling a cosmic lioness. A neon lion mane-like aura surrounds her head, radiating confidence and power. The background is illuminated with solar flares and a glowing Leo constellation, making her the center of a bold and mesmerizing cosmic stage.",
            "A zodiac warrior of Aries, clad in molten-red armor with ram's horn motifs, strides through a burning battlefield lit by constellations. Sparks arc from her shoulder plates, divine fury on her face.",
            "A Renaissance ceiling fresco reimagined as an overhead drone photo of people forming divine patterns in a desert, dust spiraling upward like angelic clouds, classical geometry shaping chaos.",
            "A neoclassical sculpture garden flooded ankle-deep in rose-colored water. Marble figures appear to weep, their tears staining the stone with golden veins that pulse in candlelight.",
            "A portrait of the wind god Aeolus painted in kinetic abstraction, his beard swirling into spirals of smoke and baroque fabric, stormclouds erupting behind him like Caravaggio gone digital.",
            "Hieronymus Bosch meets cyberpunk: biomechanical animals with cathedral architecture embedded in their backs roam a chrome valley lit by stained-glass suns.",
            "A giant hand made of honey and bones emerges from an ancient wheat field under a Turner sky. Children dressed in 19th-century garments try to climb its crystallized fingertips.",
            "A hyper-realistic oil painting of a mother combing her daughter's hair — both heads replaced with clusters of delicate glass grapes. One falls. It shatters.",
            "A surrealist chessboard set in a stormy ocean — the pawns are blindfolded prophets, the queen is on fire, and the king is missing. The board balances on a sleeping whale.",
            "A Byzantine icon reimagined in molten gold and graphite, depicting a faceless saint whose halo is a rotating eclipse, bleeding thin beams of violet light.",
            "A moonlit procession of masked figures carrying enormous baroque mirrors, each reflecting a different historical revolution, from the French to the digital.",
            "Portrait of a woman with six mouths and no eyes, whispering the secrets of ancient gods. Her hair is made of vellum scrolls, unraveling midair.",
            "An exploded-view Da Vinci sketch of a phoenix being reborn from shattered piano keys, all drawn in iron ink on oxidized parchment.",
            "A cathedral inside a seashell, lit from within by bioluminescent saints carved in coral. Its choir sings a song only visible as floating geometry in the water.",
            "An ancient Greek amphora depicting a modern protest in black-figure pottery, tear gas rendered as stylized ionic clouds. The gods look on from the border.",
            "A blindfolded child standing atop a Dürer rhinoceros, releasing doves painted in infrared. Shadows of classical columns stretch into infinity behind them.",
            "A Rococo ballroom suspended mid-explosion: dancers frozen mid-pirouette, wigs and pearls shattering like galaxies caught in reverse gravity.",
            "A Roman mosaic interpreted in glitch art — Jupiter`s thunderbolt rendered as pixelated fire, his beard drawn in ASCII, his throne levitating above a circuit-board sky.",
            "A surreal courtroom scene where the judge is a golden owl, the jury are flowers in suits, and the accused is a cloud weeping glitter onto the floor.",
            "A baroque still life of obsolete tech: rotary phones tangled with vines, cracked floppy disks alongside ancient fruit, all under chiaroscuro candlelight.",
            "A cave painting from the future: luminescent symbols sprayed on stone by drones, depicting AI worshiping extinct birds in Gregorian chant.",
            "A dreamlike corridor filled with frames: each painting inside shows you aging in reverse, until the final canvas is a single blinking eye.",
            "A medieval triptych where the angels wear modern fashion and carry megaphones, while demons take selfies beneath Gothic arches made of neon.",
            "A futuristic Venus emerging not from a shell, but from a 3D printer. Her form glitching at the edges, surrounded by floating security cameras in orbit.",
            "A zen garden made of powdered bone and volcanic ash, raked into Fibonacci spirals, watched over by robotic monks sculpted in Bauhaus minimalism.",
            "A mythological chariot race through a collapsing museum — gods drive Tesla engines, and each sculpture melts as it`s passed, forming abstract rivers.",
            "An opera stage where the singers wear hyperreal masks of extinct animals, and the music causes the background to collapse into animated Kandinsky strokes.",
            "A modern Madonna seated not with a child but a book made of fire. Around her float mathematical diagrams painted in the style of Vermeer.",
            "A silhouette of a woman whose dress becomes a village when the light hits her — roofs and steeples grow from fabric, children peek from her sleeves.",
            "A Dadaist re-creation of The Last Supper using mannequins made of vintage toys, melted crayons, and dripping velvet — all seated at a table of mirrors.",
            "A massive hourglass made of crystal containing a Renaissance battle in sand form, as each grain falls, it reshapes into a new historical moment.",
            "An epic-scale fresco of Babel interpreted as a vertical rave: spiral stairs become light beams, and the languages are coded into color and rhythm.",
            "A single teardrop floats in zero gravity, within it a miniature Flemish village lives — tiny people watch as the viewer watches back.",
            "A knight in chrome armor rides a white horse across a digital wasteland — behind them, cathedral windows open into space, showing Bosch-style visions.",
            "An art studio where each brushstroke is a living snake — the artist blindfolded, painting a giant canvas that shifts in style from cave art to cubism.",
            "A holographic shadow puppet play depicting the fall of Rome, performed on the side of a pyramid made of cracked iPads, under a purple sky.",
            "An iceberg shaped like Michelangelo`s David floats through a black sea, cracked with glowing veins, while robotic birds nest in his stone curls."
        ]
    
    @task(1)
    def check_health(self):
        """Check the health endpoint provided by nginx sidecar"""
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"Health check failed with status: {response.status_code}")
    
    @task(10)
    def flux_task(self):
        """Submit a flux task to test the inference-balancer"""
        payload = {
            "input": {
                "prompt": random.choice(self.prompts),
                "enable_base64_output": True,
                "cache_threshold": 0.1,
                "size": "1024*1024"
            }
        }

        response = self.client.post("/flux", json=payload)
        
        if response.status_code == 200:
            task_id = response.json().get("task_id")
            print(f"Task ID: {task_id}")
        else:
            print(f"Failed to submit task: {response.status_code}")