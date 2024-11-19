import os
import re
import time
from flask import Flask, render_template, send_from_directory
import openai

# Initialize Flask app
app = Flask(__name__)
app.config["SVG_FOLDER"] = os.path.join(os.getcwd(), "static/svgs")
os.makedirs(app.config["SVG_FOLDER"], exist_ok=True)  # Ensure SVG folder exists

# Set up OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

# List of 10 distinct animation ideas for Pippin
ANIMATION_IDEAS = [
    "Create an SVG of Pippin planting a tree.",
    "Create an SVG of Pippin playing tag with other unicorns.",
    "Create an SVG of Pippin ice skating on a frozen lake.",
    "Create an SVG of Pippin sunbathing on the beach.",
    "Create an SVG of Pippin surfing the waves.",
    "Create an SVG of Pippin building a snowman.",
    "Create an SVG of Pippin sledding down a hill.",
    "Create an SVG of Pippin celebrating a birthday party.",
    "Create an SVG of Pippin flying a hot air balloon.",
    "Create an SVG of Pippin dancing in the rain.",
    "Create an SVG of Pippin playing leapfrog.",
    "Create an SVG of Pippin jumping over hurdles.",
    "Create an SVG of Pippin playing chess.",
    "Create an SVG of Pippin riding a tandem bicycle.",
    "Create an SVG of Pippin performing a cheerleading routine.",
    "Create an SVG of Pippin painting graffiti art.",
    "Create an SVG of Pippin conducting a science experiment.",
    "Create an SVG of Pippin playing volleyball on the beach.",
    "Create an SVG of Pippin dancing salsa at a party.",
    "Create an SVG of Pippin doing a handstand.",
    "Create an SVG of Pippin playing the piano.",
    "Create an SVG of Pippin flying through a hoop of fire.",
    "Create an SVG of Pippin painting Easter eggs.",
    "Create an SVG of Pippin riding a Ferris wheel.",
    "Create an SVG of Pippin dancing hip-hop in a cityscape.",
    "Create an SVG of Pippin playing basketball.",
    "Create an SVG of Pippin performing a tightrope walk.",
    "Create an SVG of Pippin hosting a game show.",
    "Create an SVG of Pippin dancing with shadow puppets.",
    "Create an SVG of Pippin painting a mural on a wall.",
    "Create an SVG of Pippin playing frisbee in the park.",
    "Create an SVG of Pippin riding a carousel horse.",
    "Create an SVG of Pippin flying a pirate ship.",
    "Create an SVG of Pippin doing a hand clap dance.",
    "Create an SVG of Pippin painting abstract art.",
    "Create an SVG of Pippin riding a zip line.",
    "Create an SVG of Pippin performing a ballet dance.",
    "Create an SVG of Pippin playing the violin.",
    "Create an SVG of Pippin riding a motorcycle.",
    "Create an SVG of Pippin doing cartwheels on the beach.",
    "Create an SVG of Pippin hosting a tea party.",
    "Create an SVG of Pippin playing badminton.",
    "Create an SVG of Pippin doing tai chi in a garden.",
    "Create an SVG of Pippin juggling flaming torches.",
    "Create an SVG of Pippin riding a snow scooter.",
    "Create an SVG of Pippin performing a slam dance.",
    "Create an SVG of Pippin flying a superhero cape.",
    "Create an SVG of Pippin doing a split dance move.",
    "Create an SVG of Pippin painting with spray cans.",
    "Create an SVG of Pippin performing a mime act.",
    "Create an SVG of Pippin dancing under the stars.",
    "Create an SVG of Pippin playing hopscotch on a sidewalk.",
    "Create an SVG of Pippin doing a conga line.",
    "Create an SVG of Pippin performing a tango dance.",
    "Create an SVG of Pippin riding a tandem bike with friends.",
    "Create an SVG of Pippin doing breakdancing moves.",
    "Create an SVG of Pippin painting with watercolors.",
    "Create an SVG of Pippin riding a scooter through the city.",
    "Create an SVG of Pippin performing a drum solo.",
    "Create an SVG of Pippin dancing in a disco ball.",
    "Create an SVG of Pippin playing maracas in a band.",
    "Create an SVG of Pippin doing a belly dance.",
    "Create an SVG of Pippin riding a paddleboat on a lake.",
    "Create an SVG of Pippin performing a magic show.",
    "Create an SVG of Pippin dancing with LED lights.",
    "Create an SVG of Pippin playing the harmonica.",
    "Create an SVG of Pippin riding a surfboard on a giant wave.",
    "Create an SVG of Pippin performing a flash mob dance.",
    "Create an SVG of Pippin dancing in a field of tulips.",
    "Create an SVG of Pippin playing the xylophone.",
    "Create an SVG of Pippin riding a hoverboard.",
    "Create an SVG of Pippin performing a synchronized dance routine.",
    "Create an SVG of Pippin dancing with holographic effects.",
    "Create an SVG of Pippin playing tambourine in a folk band.",
    "Create an SVG of Pippin dancing with balloons around.",
    "Create an SVG of Pippin riding a magic carpet.",
    "Create an SVG of Pippin performing a robot dance.",
    "Create an SVG of Pippin dancing in a snowstorm.",
    "Create an SVG of Pippin playing the accordion.",
    "Create an SVG of Pippin dancing on a tightrope.",
    "Create an SVG of Pippin performing a traditional folk dance.",
    "Create an SVG of Pippin dancing amidst falling cherry blossoms.",
    "Create an SVG of Pippin playing the steel drums on a tropical island.",
    "Create an SVG of Pippin dancing with luminescent orbs.",
    "Create an SVG of Pippin performing a contemporary dance.",
    "Create an SVG of Pippin dancing with fireflies at dusk.",
    "Create an SVG of Pippin playing the bagpipes in a parade.",
    "Create an SVG of Pippin dancing through a kaleidoscope tunnel.",
    "Create an SVG of Pippin performing a traditional ballet pirouette.",
    "Create an SVG of Pippin dancing with musical notes floating around.",
    "Create an SVG of Pippin riding a mechanical bull.",
    "Create an SVG of Pippin performing a salsa dance on a dance floor.",
    "Create an SVG of Pippin dancing in a field under a full moon.",
    "Create an SVG of Pippin playing the ocarina in a magical forest.",
    "Create an SVG of Pippin dancing with colorful streamers.",
    "Create an SVG of Pippin performing a traditional cultural dance.",
    "Create an SVG of Pippin dancing amidst floating lanterns.",
]



# Function to clean SVG code by removing code fences
def clean_svg_code(svg_code):
    """
    Removes markdown code fences (```html, ```xml, and ```) from the SVG code if present.
    """
    if svg_code.startswith("```html") and svg_code.endswith("```"):
        # Remove the starting ```html and the ending ```
        svg_code = svg_code.replace("```html", "").replace("```", "").strip()
    elif svg_code.startswith("```xml") and svg_code.endswith("```"):
        # Remove the starting ```xml and the ending ```
        svg_code = svg_code.replace("```xml", "").replace("```", "").strip()
    elif svg_code.startswith("```") and svg_code.endswith("```"):
        # Remove generic code fences
        svg_code = svg_code.replace("```", "").strip()
    return svg_code

# Function to convert idea to a safe filename
def idea_to_filename(idea):
    # Convert idea to lowercase
    idea_clean = idea.lower()
    # Remove 'create an svg of pippin'
    idea_clean = idea_clean.replace('create an svg of pippin', '')
    # Remove non-alphanumeric characters
    idea_clean = re.sub(r'[^\w\s-]', '', idea_clean)
    # Replace spaces with underscores
    idea_clean = idea_clean.strip().replace(' ', '_')
    # Truncate to 50 characters
    idea_clean = idea_clean[:50]
    # Ensure filename is not empty
    if not idea_clean:
        idea_clean = 'pippin'
    filename = f"pippin_{idea_clean}.svg"
    return filename

# Function to generate SVG using OpenAI with retry logic
def generate_svg(prompt, retries=3, backoff_in_seconds=2):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # Corrected model name
            messages=[
                {
                    "role": "system",
                    "content": (f"""
You are an expert designer at generating animated SVGs of a unicorn named Pippin, which you will save and provide back to the user. Based on the user request, provide back SVG (either still or animated) that captures the user's request. Analyze the wobbly pattern of Pippin as inspiration. When animating Pippin, make sure that parts of the head (mane, ears, eyes, horn) always move with the head unless you are specifically trying to move one of the parts. You can make eyes blink/close by turning them into an eye. Hooves should always stay attached to the leg. Be mindful of position of various parts as you animate them. Make sure to color new objects that are introduced. Change the background to match the topic and don't hesitate to introduce new items. Here is his base SVG:

<svg width="250" height="250" viewBox="0 0 250 250" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="250" height="250" fill="#f0f8ff"></rect>

  <!-- Steady Legs Group -->
  <g>
    <!-- Legs -->
    <path d="M100,160 L100,190" stroke="#000" stroke-width="2"></path>
    <path d="M120,160 L120,190" stroke="#000" stroke-width="2"></path>
    <path d="M140,160 L140,190" stroke="#000" stroke-width="2"></path>
    <path d="M160,120 Q165,140 160,160" stroke="#000" stroke-width="2"></path>

    <!-- Hooves -->
    <ellipse cx="100" cy="190" rx="5" ry="2" fill="#000"></ellipse>
    <ellipse cx="120" cy="190" rx="5" ry="2" fill="#000"></ellipse>
    <ellipse cx="140" cy="190" rx="5" ry="2" fill="#000"></ellipse>
    <ellipse cx="160" cy="160" rx="5" ry="2" fill="#000"></ellipse>
  </g>

  <!-- Body Group -->
  <g>
    <animateTransform
      attributeName="transform"
      attributeType="XML"
      type="translate"
      values="0 0; 0 15; 0 0"
      dur="0.8s"
      repeatCount="indefinite"
    />

    <!-- Unicorn Body -->
    <path d="M80,150 Q60,120 80,90 Q100,60 140,70 Q180,80 160,120 Q150,160 100,160 Z" fill="#fff" stroke="#000" stroke-width="2"></path>

    <!-- Tail -->
    <path d="M80,150 Q70,155 75,160 Q70,165 80,170" stroke="#ff69b4" stroke-width="2" fill="none"></path>
    <path d="M75,160 Q80,165 75,170" stroke="#ff69b4" stroke-width="2" fill="none"></path>

    <!-- Details on Body -->
    <path d="M90,120 Q95,110 100,120" stroke="#000" stroke-width="1" fill="none"></path>
    <path d="M110,130 Q115,120 120,130" stroke="#000" stroke-width="1" fill="none"></path>
  </g>

  <!-- Head Group -->
  <g>
    <animateTransform
      attributeName="transform"
      attributeType="XML"
      type="translate"
      values="0 0; 0 12; 0 0"
      dur="0.8s"
      begin="0.08s"
      repeatCount="indefinite"
    />

    <!-- Unicorn Head and Neck -->
    <path d="M140,70 Q150,60 160,55 Q170,50 175,60 Q180,70 170,80 Q160,85 150,80 Q140,75 140,70 Z" fill="#fff" stroke="#000" stroke-width="2"></path>

    <!-- Horn -->
    <polygon points="160,55 155,35 165,35" fill="#ffd700" stroke="#000" stroke-width="1"></polygon>

    <!-- Ears -->
    <path d="M165,45 Q166,40 160,43" fill="#fff" stroke="#000" stroke-width="1"></path>
    <path d="M170,45 Q171,40 165,43" fill="#fff" stroke="#000" stroke-width="1"></path>

    <!-- Eyes -->
    <circle cx="162" cy="60" r="3" fill="#000"></circle>
    <circle cx="158" cy="60" r="1.5" fill="#fff"></circle>

    <!-- Mane -->
    <path d="M155,55 Q150,60 155,65 Q150,70 155,75 Q150,80 155,85" stroke="#ff69b4" stroke-width="2" fill="none"></path>
    <path d="M160,55 Q155,60 160,65 Q155,70 160,75 Q155,80 160,85" stroke="#ff69b4" stroke-width="2" fill="none"></path>
  </g>
</svg>

Create the SVG, save it, and provide the link back to user where they can view the animation. Only provide the SVG code in your response with no decorators before or after.
                    """
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        svg_code = response.choices[0].message.content.strip()
        svg_code = clean_svg_code(svg_code)  # Clean the SVG code
        return svg_code
    except Exception as e:
        if retries > 0:
            time.sleep(backoff_in_seconds)
            return generate_svg(prompt, retries - 1, backoff_in_seconds * 2)
        else:
            print(f"Failed to generate SVG for prompt '{prompt}' due to rate limits.")
            return None

# Generate and save all SVGs serially
def generate_batch_of_svgs():
    for i, idea in enumerate(ANIMATION_IDEAS):
        svg_filename = os.path.join(app.config["SVG_FOLDER"], idea_to_filename(idea))
        if os.path.exists(svg_filename):
            print(f"SVG already exists: {svg_filename}. Skipping generation.")
            continue
        svg_content = generate_svg(idea)
        if svg_content:
            try:
                with open(svg_filename, "w") as svg_file:
                    svg_file.write(svg_content)
                print(f"Generated: {svg_filename}")
            except IOError as io_err:
                print(f"IOError when writing SVG file '{svg_filename}': {io_err}")
        else:
            print(f"Failed to generate SVG for: {idea}")

# Route to display all SVGs in the folder
@app.route("/")
def index():
    try:
        svg_files = os.listdir(app.config["SVG_FOLDER"])
        svg_files = [f for f in svg_files if f.endswith(".svg")]
        return render_template("index.html", svgs=svg_files)
    except Exception as e:
        return f"An error occurred while listing SVGs: {e}", 500

# Route to serve individual SVG files
@app.route("/svgs/<filename>")
def serve_svg(filename):
    try:
        return send_from_directory(app.config["SVG_FOLDER"], filename)
    except FileNotFoundError:
        return "SVG file not found.", 404
    except Exception as e:
        return f"An error occurred while serving SVG: {e}", 500

print("Starting app and generating SVGs...")
generate_batch_of_svgs()

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
