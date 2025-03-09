import streamlit as st
import boto3
import base64
import json
import logging
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

sns_client = boto3.client('sns')
bedrock_runtime = boto3.client('bedrock-runtime')
cloudformation = boto3.resource('cloudformation')

def get_cloudformation_output(stack_name, output_key):
    stack = cloudformation.Stack(stack_name)
    for output in stack.outputs:
        if output['OutputKey'] == output_key:
            return output['OutputValue']
    return None

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()
            base64_image = base64.b64encode(image_content).decode('utf-8')
            return base64_image
    except Exception as e:
        logger.error(f"Error reading image from local file system: {e}")
        return None

few_shot_examples = [
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": get_base64_image("few_shot_images/spill.jpg")
        }
    },
    {
        "type": "text",
        "text": "CLEANING: The image shows a spill on the shop floor. CLEANING department, please bring a mop to clean up the spill."
    },
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": get_base64_image("few_shot_images/debris.jpg")
        }
    },
    {
        "type": "text",
        "text": "CLEANING: There is debris scattered on the shop floor. CLEANING department, please bring a broom to sweep up the debris."
    },
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": get_base64_image("few_shot_images/dim_lighting.jpg")
        }
    },
    {
        "type": "text",
        "text": "LIGHTING: The lighting in the shop floor area appears to be dim. LIGHTING department, please adjust the lighting to ensure proper visibility."
    },
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": get_base64_image("few_shot_images/fight.jpg")
        }
    },
    {
        "type": "text",
        "text": "SAFETY: There is an altercation occurring on the shop floor. SAFETY, please respond immediately to de-escalate the situation. Weapons are visible."
    },
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": get_base64_image("few_shot_images/injury.jpg")
        }
    },
    {
        "type": "text",
        "text": "SAFETY: An employee appears to be injured on the shop floor. They are clutching their arm and seem to be in pain. SAFETY, please call an ambulance for medical assistance."
    },
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": get_base64_image("few_shot_images/fire.jpg")
        }
    },
    {
        "type": "text",
        "text": "SAFETY: There is a fire on the shop floor. SAFETY, please respond immediately to extinguish the fire and ensure the safety of all personnel."
    },
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": get_base64_image("few_shot_images/normal.jpg")
        }
    },
    {
        "type": "text",
        "text": "GOOD: The shop floor appears to be in normal condition. GOOD, no immediate action is required"
    }
]

def analyze_image(image, few_shot_examples, prompt):
    try:
        # Payload for Bedrock Runtime
        payload = {
            "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": few_shot_examples + [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        }

        # Convert the payload to bytes
        body_bytes = json.dumps(payload['body']).encode('utf-8')

        # Invoke the Bedrock Runtime model
        response = bedrock_runtime.invoke_model(
            body=body_bytes,
            contentType=payload['contentType'],
            accept=payload['accept'],
            modelId=payload['modelId']
        )

        # Process the response from Bedrock Runtime
        response_body = json.loads(response['body'].read().decode('utf-8'))
        
        # Extract the relevant text from the response
        relevant_text = response_body['content'][0]['text']
        
        return relevant_text
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return "An error occurred during image analysis."
    
def send_to_sns(keyword, message):
    topic_arn = ""
    if keyword == "SAFETY":
        topic_arn = get_cloudformation_output('qcomply-cft', 'SafetyTopicArn')
    elif keyword == "CLEANING":
        topic_arn = get_cloudformation_output('qcomply-cft', 'CleaningTopicArn')
    elif keyword == "LIGHTING":
        topic_arn = get_cloudformation_output('qcomply-cft', 'LightingTopicArn')
    elif keyword == "GOOD":
        topic_arn = get_cloudformation_output('qcomply-cft', 'GoodTopicArn')

    if topic_arn:
        try:
            response = sns_client.publish(
                TopicArn=topic_arn,
                Message=message
            )
            logger.info(f"Message sent to SNS topic: {topic_arn}")
        except Exception as e:
            logger.error(f"Error sending message to SNS: {e}")

def main():
    st.title("AI-Vision")
    st.subheader("AI-Vision Instructions")
    default_prompt = "Analyze this photo from the perspective of a Shop Floor Manager.  As a Shop Floor manager you need to ensure the shop floor is relatively clean and safe. Based on what you observe, conclude with one of the following actions by starting your response with one chosen KEYWORD: CLEANING: (for anything dirty or spilled), LIGHTING: (if the room is too dark, suggest adding light), SAFETY: (if there's any scene of injury, fighting, lack or protective gear), or GOOD: (if everything looks relatively safe, and clean). Provide concise reasoning for your conclusion and offer concise suggestions for immediate actions the staff should take, if any."
    prompt = st.text_area("How would you like your images analyzed?:", value=default_prompt, height=175)

    st.subheader("Image to Analyze")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = base64.b64encode(uploaded_file.read()).decode('utf-8')
        
        # Display the uploaded image
        img = Image.open(io.BytesIO(base64.b64decode(image)))
        st.image(img, caption='Uploaded Image', use_column_width=True)

        if st.button("Analyze"):
            with st.spinner("Analyzing image..."):
                result = analyze_image(image, few_shot_examples, prompt)
                st.write(result)

                # Extract the keyword from the response
                keyword = result.split(":")[0]
                send_to_sns(keyword, result)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error running the application: {e}")
        st.error("An error occurred. Please check the logs for more details.")