import os
import openai
import base64
from flask import Flask, request, render_template, redirect, url_for

# Initialize Flask app
app = Flask(__name__)


openai.api_key = "api-key"

# Helper function to encode image as base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Define the route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Define the route to handle the form submission
@app.route('/analyze', methods=['POST'])
def analyze():
    # Get allergens from the form input
    allergens = request.form.get('allergens')

    # Get the uploaded image
    image = request.files['imageInput']

    # Save the image to a temporary file
    image_path = os.path.join("uploads", image.filename)
    image.save(image_path)

    # Encode the image as base64
    base64_image = encode_image(image_path)

    # Prepare the GPT system message
    system_message1 = """
    The GPT will receive an image. It will first identify whether the image is a readable food label with ingredients, or if it is something else.
    If the image is blurry, it will inform the user that it is blurry.
    If the image is not a food label, it will say so.
    If it is a readable ingredient list on a food label, the GPT will look at the provided allergens and check the ingredient list for both exact matches and related terms or misspellings to determine if the allergen is present in the food.
    It will then out put the text exactly like this:
    Allergens Present:
    1. Allergen 1  - Present/ Not Present (and  gpt will say "listed in ingedients as (ingredient)")
    2. Alergen 2 - Present/ Not Present (and  gpt will say "listed in ingedients as (ingredient)")
    3. Allergen 3 - Present/ Not Present (and  gpt will say "listed in ingedients as (ingredient)")
    4. Allergen 4 - Present/ Not Present (and  gpt will say "listed in ingedients as (ingredient)")
    5... etc

    Harmul Ingredients (gpt will list the harmful ingredients/dyes/preservatives in red and a short phrase why they are harmful):
    1. Harmful Ingredient 1 - Reason
    2. Harmful Ingredient 2 - Reason
    3. Harmful Ingredient 3 - Reason
    4... etc keep listing how every many harmful ingredients there are

    That is all it is doing in that fortmat. Make sure to keep the line breaks and also bold the titles (Allergens Present and Hamful Ingredients). Do not bold anything except the titles.
    If the user says they dont have any allergens, just put no allergens given under the allergens present section and just list harful ingredients.
    """

    system_message = """
Image Assessment:

First, it will determine if the image is a readable food label containing an ingredient list.
If the image is blurry, it will inform the user with the message: "The image appears blurry and cannot be read properly."
If the image is not a food label, it will state: "The image provided is not a food label."
If the image contains a readable ingredient list, it will proceed to the next steps.

Allergen Check:
The GPT will analyze the provided list of allergens and check for their presence in the ingredient list.
It will identify both exact matches and related terms or common misspellings to ensure a thorough search.
If no allergens are provided by the user, GPT will display "No allergens given."
Output for allergens should be formatted as follows:

Allergens Present:
Allergen 1 - Present/Not Present (listed in ingredients as "ingredient")
Allergen 2 - Present/Not Present (listed in ingredients as "ingredient")
Allergen 3 - Present/Not Present (listed in ingredients as "ingredient")
Allergen 4 - Present/Not Present (listed in ingredients as "ingredient")
... keep going for however many allergens there are


Harmful Ingredient Identification:
GPT will analyze the ingredient list to identify harmful ingredients, including preservatives, artificial dyes, and other substances known to have adverse health effects.
It will output these harmful ingredients in red text, along with a short explanation of why they are harmful.
Format the harmful ingredient section as follows:

Harmful Ingredients:
Harmful Ingredient 1 - Reason for being harmful
Harmful Ingredient 2 - Reason for being harmful
Harmful Ingredient 3 - Reason for being harmful
... keep going for however many harmful ingredients there are

Make sure to follow this structure exactly, preserving line breaks, and bolding the section titles ("Allergens Present" and "Harmful Ingredients") as well as the ingredient names in the allergens and in the harmful ingredients section. Makre sure to bold all the allergens and all the harfmful ingredients. If no allergens are provided, skip the allergen checks and proceed directly to the harmful ingredients section.
"""

    # Prepare the user text
    user_text = f"Please analyze the attached food label. The allergens are {allergens}"

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],

                    }
        ],
            max_tokens=1000
            )

    # Get the result from the GPT response
    result_text = response.choices[0].message.content

    # Replace the first `**` with `<b>` and the second with `</b>`, to make titles bold
    while "**" in result_text:
        result_text = result_text.replace("**", "<b>", 1).replace("**", "</b>", 1)
    # Replace newlines with HTML line breaks
    result_text = result_text.replace("\n", "<br>")

    # Delete the temporary uploaded file
    os.remove(image_path)

    # Return the result to the web page
    return render_template('index.html', response=result_text)

if __name__ == '__main__':
    # Ensure the uploads directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
