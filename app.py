import streamlit as st
import boto3
import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from openai import OpenAI

st.set_page_config(page_title="AI CloudOps Dashboard", layout="wide")

st.title("AI-Powered CloudOps & Incident Intelligence Platform")

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

INSTANCE_ID = "i-02a88d91a43e460ad"

response = cloudwatch.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': INSTANCE_ID
        },
    ],
    StartTime=datetime.utcnow() - timedelta(hours=2),
    EndTime=datetime.utcnow(),
    Period=300,
    Statistics=['Average']
)

datapoints = response['Datapoints']

cpu_values = []

for point in datapoints:
    cpu_values.append(point['Average'])

cpu = 0

if cpu_values:
    cpu = round(cpu_values[-1], 2)

# ML Anomaly Detection
anomaly_detected = False

if len(cpu_values) > 5:

    data = np.array(cpu_values).reshape(-1, 1)

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    model.fit(data)

    prediction = model.predict(data)

    if prediction[-1] == -1:
        anomaly_detected = True

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

ai_rca = "No active incidents detected."

if anomaly_detected:

    prompt = f"""
    EC2 CPU anomaly detected.

    Current CPU metrics:
    {cpu_values}

    Generate professional Root Cause Analysis
    for cloud infrastructure incident.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_rca = response.choices[0].message.content

st.subheader("Real-Time Infrastructure Monitoring")

col1, col2 = st.columns(2)

col1.metric("EC2 CPU Usage", f"{cpu}%")
col2.metric("Monitoring Status", "Active")

if anomaly_detected:
    st.error("ML Anomaly Detected in Infrastructure")
else:
    st.success("Infrastructure Healthy")

st.subheader("AI Incident Intelligence")

st.write(ai_rca)

st.subheader("Infrastructure Metrics")

df = pd.DataFrame({
    "CPU Utilization": cpu_values
})

st.line_chart(df)
