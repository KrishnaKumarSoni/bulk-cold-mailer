import openai
from config import OPENAI_API_KEY
import re
import json
import logging

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

def generate_personalized_email(
    company_name, company_info, person_name, person_headline, person_about,
    on_behalf_of, background_info, call_to_action, closing
):
    prompt = f"""
    You are an expert in writing friendly, casual, and to-the-point cold emails. Your task is to generate a short, casual, personalized cold email on behalf of {on_behalf_of}, based on the following company information, founder details, and the capabilities.

    Company Name:
    {company_name}

    Company Information:
    {company_info}

    Founder's Name:
    {person_name}

    Founder's Headline:
    {person_headline}

    Founder's About:
    {person_about}

    Background Information:
    {background_info}

    Call to action:
    {call_to_action}

    Email closing:
    {closing}

    Writing style: conversational, casual, engaging, simple to read, simple linear active voice sentences, informational and insightful.
    
    Use the following formulas to write effective cold emails:

    1. AIDA: Start with an attention-grabbing subject line or opening sentence. Highlight the recipient's pain points to build interest. List the benefits and use social proof, scarcity, or exclusivity to create desire. End with a specific call to action.

    2. BBB: Keep the email brief, blunt, and basic. Shorten the email, get straight to the point, and use simple language.

    3. PAS: Identify a sore point (Problem). Emphasize the severity with examples or personal experience (Agitate). Present your solution (Solve).

    4. QVC: Start with a question. Highlight what makes you unique (Value Proposition). End with a strong call to action.

    5. PPP: Open with a genuine compliment (Praise). Show how your product/service helps (Picture). Encourage them to take action (Push).

    6. SCH: Introduce your product or idea (Star). Provide strong facts and reasons (Chain). End with a powerful call to action (Hook).

    7. SSS: Introduce the star of your story (Star). Describe the problem they face (Story). Explain how your product solves the problem (Solution).

    8. RDM: Use facts (Fact-packed), be brief (Telegraphic), be specific (Specific), avoid too many adjectives (Few adjectives), and make them curious (Arouse curiosity).

    These formulas will help you craft concise, casual, friendly engaging, and compelling cold emails.

    Respond with a JSON containing the subject and email content only in the following format:
    {{
      "subject": "<subject line>",
      "email": "<email content>"
    }}
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        response_content = response.choices[0].message.content.strip()
    except openai.APIError as e:
        logging.error(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.APIConnectionError as e:
        logging.error(f"Failed to connect to OpenAI API: {e}")
        pass
    except openai.RateLimitError as e:
        logging.error(f"OpenAI API request exceeded rate limit: {e}")
        pass

    # Use the new function to extract the email subject and body from the response
    email_data = extract_email_subject_and_body(response_content)
    return email_data

def extract_email_subject_and_body(email_text):
    # Clean and correct the JSON format
    email_text = email_text.replace('\n', '')
    email_text = re.sub(r'\\n', '', email_text)

    # Use regex to extract the JSON response
    json_pattern = re.compile(r"\{.*\}", re.DOTALL)
    json_match = json_pattern.search(email_text)
    
    if json_match:
        email_json = json_match.group(0)
        email_data = json.loads(email_json)
        return email_data
    else:
        return {"subject": "No subject found", "email": "No email content found"}

def convert_to_html(plain_text):
    prompt = f"""
    Convert the following plain text email to HTML. Ensure to handle new line breaks with <br><br> tags and make links clickable.

    Plain Text:
    {plain_text}

    Use only <br><br> tags to replace new line breaks and anchor tags for links and no other html element. Respond with just the converted content.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        response_content = response.choices[0].message.content.strip()
    except openai.APIError as e:
        logging.error(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.APIConnectionError as e:
        logging.error(f"Failed to connect to OpenAI API: {e}")
        pass
    except openai.RateLimitError as e:
        logging.error(f"OpenAI API request exceeded rate limit: {e}")
        pass

    # Extract HTML content from the first greeting to the last </a> tag or end of the text
    html_match = re.search(r'(Hi|Hello|Dear|Greetings|Hey|Hope).*?(</a>|$)', response_content, re.DOTALL)
    if html_match:
        start_pos = html_match.start()
        end_pos = max([m.end() for m in re.finditer(r'</a>', response_content)]) if '</a>' in response_content else len(response_content)
        html_content = response_content[start_pos:end_pos].strip()
        return html_content
    else:
        raise ValueError("No valid HTML content found in the response")
