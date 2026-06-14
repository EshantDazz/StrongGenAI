# Deploying Weather MCP Server to AWS — Self Study Guide

The goal: get `weather.py` running on AWS so that the `/mcp` endpoint is publicly accessible from anywhere — your laptop, any agent, any tool.

There are two practical paths for self-study:

| Path | Effort | Cost | Best for |
|---|---|---|---|
| **EC2 (direct)** | Low | ~$5/mo (t3.micro) | Learning the basics |
| **Docker + EC2** | Medium | ~$5/mo | Learning containers too |

This guide covers both. Start with EC2 direct — Docker is the bonus section at the end.

---

## Architecture Overview

```
Your laptop / any tool
        |
        | HTTP POST to http://<EC2-PUBLIC-IP>:8000/mcp
        |
   ┌────▼─────────────────────┐
   │  AWS EC2 Instance         │
   │  Ubuntu 24.04             │
   │                           │
   │  python weather.py        │
   │  FastMCP on 0.0.0.0:8000  │
   └───────────────────────────┘
        |
   Security Group: port 8000 open to 0.0.0.0/0
```

---

## Prerequisites

- AWS account (free tier works)
- AWS CLI installed locally: `brew install awscli`
- Your `weather.py` and a `requirements.txt`

---

## Step 1 — Create a requirements.txt

In your `mcp/` folder, create this file so the EC2 instance knows what to install:

```
# mcp/requirements.txt
mcp[cli]
fastmcp
uvicorn
```

---

## Step 2 — Launch an EC2 Instance

### 2a. Go to AWS Console → EC2 → Launch Instance

Fill in:

| Field | Value |
|---|---|
| Name | `weather-mcp-server` |
| AMI | Ubuntu Server 24.04 LTS (free tier eligible) |
| Instance type | `t3.micro` (free tier) |
| Key pair | Create a new one → download the `.pem` file → save it somewhere safe |
| Network settings | Keep default VPC |

### 2b. Configure Security Group (critical step)

This controls who can reach your server. Add these inbound rules:

| Type | Protocol | Port | Source | Why |
|---|---|---|---|---|
| SSH | TCP | 22 | My IP | So you can connect to manage it |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | So the MCP endpoint is publicly reachable |

> For self-study, opening 8000 to `0.0.0.0/0` is fine. For anything real, you'd lock this down.

Click **Launch Instance**.

---

## Step 3 — SSH Into the Instance

Once the instance shows "Running", grab its **Public IPv4 address** from the EC2 console.

```bash
# Fix key permissions (required by SSH)
chmod 400 /path/to/your-key.pem

# SSH in
ssh -i /path/to/your-key.pem ubuntu@<EC2-PUBLIC-IP>
```

You are now inside the EC2 machine.

---

## Step 4 — Install Python and Dependencies

Run these commands inside the EC2 terminal:

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv -y

# Verify
python3 --version
```

---

## Step 5 — Upload Your Code to EC2

**Option A — From your local machine** (run this on your laptop, not EC2):

```bash
scp -i /path/to/your-key.pem \
    mcp/weather.py \
    mcp/requirements.txt \
    ubuntu@<EC2-PUBLIC-IP>:~/
```

**Option B — If your code is on GitHub** (run this on EC2):

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo/mcp
```

---

## Step 6 — Set Up Virtual Environment and Install Packages

Back in the EC2 terminal:

```bash
# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 7 — Run the Weather Server

```bash
# Make sure you're in the directory with weather.py
python3 weather.py
```

You should see:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Your MCP server is now live at:

```
http://<EC2-PUBLIC-IP>:8000/mcp
```

---

## Step 8 — Test It From Your Laptop

Open a new terminal on your laptop and run:

```bash
curl -X POST http://<EC2-PUBLIC-IP>:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

If you get back a JSON response listing the `get_weather` tool, the server is working.

---

## Step 9 — Update client.py to Use the Cloud URL

Change the `weather` config in `client.py` from localhost to your EC2 address:

```python
client = MultiServerMCPClient({
    "math": {
        "command": "python",
        "args": ["mcp/mathsserver.py"],
        "transport": "stdio",
    },
    "weather": {
        "url": "http://<EC2-PUBLIC-IP>:8000/mcp",   # <-- EC2 public IP here
        "transport": "streamable-http",
    },
})
```

Now run the client from your laptop:

```bash
python mcp/client.py
```

It connects to the math server locally (stdio) and the weather server on AWS (HTTP). Both tools are available to the agent.

---

## Step 10 — Keep the Server Running After You Close SSH

Right now the server dies when you close the SSH session. Fix this with `nohup`:

```bash
# Run in background, logs go to weather.log
nohup python3 weather.py > weather.log 2>&1 &

# Check it started
cat weather.log

# See the process ID
ps aux | grep weather.py
```

To stop it later:

```bash
pkill -f weather.py
```

---

## Step 11 — Auto-Start on Reboot (Optional but Good to Know)

Create a systemd service so it restarts automatically if the EC2 instance reboots:

```bash
sudo nano /etc/systemd/system/weather-mcp.service
```

Paste this (adjust paths to match where your files are):

```ini
[Unit]
Description=Weather MCP Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/home/ubuntu/venv/bin/python3 /home/ubuntu/weather.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-mcp
sudo systemctl start weather-mcp

# Check status
sudo systemctl status weather-mcp
```

---

## Bonus: Docker Approach (Cleaner, More Portable)

If you want to learn Docker alongside this:

### Dockerfile (create this in mcp/)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY weather.py .

EXPOSE 8000

CMD ["python", "weather.py"]
```

### Build and Run Locally First

```bash
cd mcp/
docker build -t weather-mcp .
docker run -p 8000:8000 weather-mcp
```

Test it at `http://localhost:8000/mcp` — same as before.

### Deploy Docker Image to EC2

On your laptop, copy the image to EC2:

```bash
# Save image to a tar file
docker save weather-mcp | gzip > weather-mcp.tar.gz

# Upload to EC2
scp -i /path/to/your-key.pem weather-mcp.tar.gz ubuntu@<EC2-PUBLIC-IP>:~/
```

On EC2:

```bash
# Install Docker
sudo apt install docker.io -y
sudo systemctl start docker
sudo usermod -aG docker ubuntu   # then log out and back in

# Load and run the image
docker load < weather-mcp.tar.gz
docker run -d -p 8000:8000 --restart always --name weather-mcp weather-mcp
```

The `--restart always` flag replaces the systemd setup — Docker handles restarts automatically.

---

## Cost Estimate (Self Study)

| Resource | Monthly Cost |
|---|---|
| t3.micro EC2 (always on) | ~$8/mo |
| t3.micro EC2 (stopped when not in use) | ~$0.10/mo (just EBS storage) |
| Free tier (first 12 months) | 750 hrs/mo t2.micro free |

**Tip for self-study:** Stop the instance when you're not using it. You only pay for EBS storage (~$0.10/mo) when stopped. Start it again when you need it — the public IP will change unless you attach an Elastic IP.

---

## Elastic IP (Keep the Same URL Forever)

Every time you stop/start EC2, the public IP changes. To get a fixed IP:

1. EC2 Console → Elastic IPs → Allocate Elastic IP
2. Associate it with your instance
3. Use that IP in `client.py` — it never changes even after reboots

Elastic IPs are free as long as they are attached to a running instance.

---

## Quick Reference

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@<EC2-IP>

# Start server (foreground)
python3 weather.py

# Start server (background)
nohup python3 weather.py > weather.log 2>&1 &

# Check logs
tail -f weather.log

# Stop server
pkill -f weather.py

# Test endpoint
curl -X POST http://<EC2-IP>:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```
