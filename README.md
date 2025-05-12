# Healthcare Appointment Chatbot
---
**Project Description:**

Develop a healthcare chatbot to automate customer service at clinics, enhance user experience, and optimize operational efficiency. The chatbot provides quick access to appointment schedules, clinic services, and doctor details while reducing the workload for customer support staff. Additionally, it supports data management and sends automated reminders to patients.

**Key features:**
- Interface: A simple, user-friendly website that displays clinic 
information and supports appointment scheduling.
- Answer customer questions about clinic services, working hours, and 
doctors. 
- Schedule/ Search/ Cancel appointments and send SMS notifications. 
- Store appointment information in the database for easy 
management.

[📄 Xem tài liệu PDF](Final_project_report.pdf)

## 🚀 How to Run the Project
### 📥 Clone the Repository
    git clone https://github.com/dduyds/Healthcare-Appointment-Chatbot.git
    cd Healthcare-Appointment-Chatbot

### 🔧 Run Without Docker
1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
2. **Start Rasa Server**
   ```bash
   rasa run --cors "*"
3. **Start Action Server**
   ```bash
   rasa run actions
4. **Chat with the bot**
   ```bash
   http://localhost:8000/index.html
###  🐳 Run With Docker
1. **Build Docker image**
   ```bash
   docker build -t rasa-chatbot .
2. **Run Docker container**
   ```bash
   docker run -p 5005:5005 -p 5055:5055 -p 8000:8000 rasa-chatbot
3. **Chat with the bot**
   ```bash
   http://localhost:8000/index.html
