# AI-Vision

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg" alt="Framework">
  <img src="https://img.shields.io/badge/AWS-Bedrock%20%7C%20SNS-232F3E.svg" alt="AWS Services">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

A Streamlit app that utilizes AWS Bedrock (Claude 3 Sonnet) to analyze images from warehouses and shop floors, automatically sending notifications to the relevant teams through SNS when issues are identified

![image](https://github.com/user-attachments/assets/259c91ad-984d-4c56-b80a-77127c1a578f)

## 🔍 Overview

AI-Vision will automatically categorizes uploaded images into one of four categories:

- **Cleaning** - Issues that require janitorial attention
- **Safety** - Hazards or safety violations that need immediate action
- **Lighting** - Problems with illumination or electrical systems
- **AllGood** - Images with no detected issues (catch-all category)


## 🛠️ Prerequisites

- Python 3.x
- AWS account with permissions for:
  - SNS
  - CloudFormation
  - Bedrock
- AWS Region: **us-west-2**
- Bedrock access with Claude 3 Sonnet model enabled

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/lazer-eye-development/ai-vision.git
cd ai-vision
```

### 2. Set up a virtual environment (Optional)

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Deploy AWS resources with CloudFormation

The included template (`ai-vision-cft.yaml`) will create:
- 4 SNS Topics (Cleaning, Safety, Lighting, and Good)
- AI-Shop-Floor-Manager IAM user with required permissions

**Deployment steps:**
1. Open the AWS CloudFormation console
2. Click "Create stack" → "With new resources (standard)"
3. Select "Upload a template file" and choose the `ai-vision-cft.yaml` file
4. Set the stack name to `ai-vision-cft` (required)
5. Complete the stack creation process

### 5. Post-deployment configuration
- Manually subscribe an email address to each of the four SNS Topics
- Create an access key for the new AI-Shop-Floor-Manager IAM user
- Configure AWS CLI with the new credentials:
  ```bash
  aws configure
  ```
  > **Important:** You must use the `us-west-2` region when configuring

### 6. Launch the application
```bash
streamlit run app.py
```

### 7. Access the application
Open your web browser and navigate to: http://localhost:8501

## 📊 Usage

1. **Upload an image** - Select a sample image from the `few_shot_images` folder
2. **Analyze the image** - Click the "Analyze" button to process the image
3. **Review results** - The analysis will be displayed on screen
4. **Automatic notification** - An SNS notification will be automatically sent to the appropriate team

You can modify the application's prompt to customize how the AI analyzes and categorizes the images.

## 📝 Customization

The application is designed with flexibility in mind:
- Adjust the AI prompt to refine image analysis criteria
- Modify SNS topics to match your organization's structure
- Add new categories by updating both the application and CloudFormation template

## 🔒 Security

The ai-visionr IAM user is configured with least privilege access, only having permissions necessary for the application to function.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <small>Making warehouse management smarter with AWS AI services</small>
</p>
