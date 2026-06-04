import os
import io
import json
from flask import Flask, render_template_string, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)

# --- ENTERPRISE KNOWLEDGE BASE ---
COLLEGE_DB = {
    "NITK": {
        "name": "National Institute of Technology Karnataka (NITK Surathkal)",
        "location": "Surathkal, Mangalore",
        "fee": "Rs. 1,50,000/year",
        "type": "National Importance Tier-1",
        "logo_bg": "#1E3A8A", "logo_txt": "NITK",
        "highlight": "Ranked among India's top tech institutes. Elite research facilities and ocean-side campus layout."
    },
    "RVCE": {
        "name": "RV College of Engineering (RVCE)",
        "location": "Mysore Road, Bangalore",
        "fee": "Rs. 2,50,000/year (KCET Merit)",
        "type": "Autonomous VTU Affiliated",
        "logo_bg": "#065F46", "logo_txt": "RVCE",
        "highlight": "Ranked #1 in Bangalore for placements. Elite hardware architectures and industry partnerships."
    },
    "PESU": {
        "name": "PES University (PESU RR Campus)",
        "location": "Ring Road, Bangalore",
        "fee": "Rs. 4,50,000/year (PESSAT Track)",
        "type": "Private State University",
        "logo_bg": "#991B1B", "logo_txt": "PESU",
        "highlight": "Ultra-modern infrastructure, premium tech clusters, and phenomenal placement package track records."
    },
    "MSRIT": {
        "name": "Ramaiah Institute of Technology (MSRIT)",
        "location": "MSR Nagar, Bangalore",
        "fee": "Rs. 2,45,000/year (KCET Merit)",
        "type": "Autonomous VTU Affiliated",
        "logo_bg": "#374151", "logo_txt": "MSRIT",
        "highlight": "Outstanding legacy faculty networks, exceptional IT frameworks, and stellar placement records."
    },
    "BMSCE": {
        "name": "BMS College of Engineering (BMSCE)",
        "location": "Basavanagudi, Bangalore",
        "fee": "Rs. 2,40,000/year (KCET Merit)",
        "type": "Autonomous VTU Affiliated",
        "logo_bg": "#854D0E", "logo_txt": "BMSCE",
        "highlight": "One of India's oldest legacy institutions with deep global technical alumni reach."
    },
    "SJCIT": {
        "name": "Sri Jagadguru Chandrashekaranatheshwara Institute of Technology (SJCIT)",
        "location": "Chikkaballapur, Bangalore Region",
        "fee": "Rs. 1,10,000/year (Affordable VTU)",
        "type": "VTU Affiliated Elite Choice",
        "logo_bg": "#0369A1", "logo_txt": "SJCIT",
        "highlight": "Outstanding institutional support, sprawling eco-campus, and fantastic value placement pathways."
    },
    "GOVT": {
        "name": "Government Engineering College (GEC)",
        "location": "State Designated Centers, Karnataka",
        "fee": "Rs. 45,000/year (Subsidized)",
        "type": "State Government Run",
        "logo_bg": "#1E293B", "logo_txt": "GEC",
        "highlight": "Highly subsidized fees managed entirely by the state allotment panel."
    }
}

# --- ANALYTICS MACHINE LOGIC ---
def process_analytics(percentage, budget, interest):
    if percentage >= 96:
        kcet = int((100 - percentage) * 350 + 40)
        jee = round(98.8 + (percentage - 96) * 0.28, 2)
        chance, status, col = 96, "TIER-1 EXCELLENCE MATCH", "success"
    elif percentage >= 88:
        kcet = int((96 - percentage) * 1100 + 1450)
        jee = round(93.0 + (percentage - 88) * 0.70, 2)
        chance, status, col = 80, "STRONG MERIT COMPATIBILITY", "primary"
    elif percentage >= 75:
        kcet = int((88 - percentage) * 2200 + 10250)
        jee = round(82.0 + (percentage - 75) * 0.82, 2)
        chance, status, col = 55, "MODERATE SEAT MATCH", "warning"
    else:
        kcet = int((75 - percentage) * 3200 + 38850)
        if kcet > 120000: kcet = 124500
        jee = max(15.0, round(55.0 + (percentage - 55) * 1.35, 2))
        chance, status, col = 25, "PROBATIONAL ADMISSION BRACKET", "danger"

    if kcet <= 1000 and budget == "High": selected = COLLEGE_DB["NITK"]
    elif kcet <= 3000 and budget == "High": selected = COLLEGE_DB["RVCE"]
    elif kcet <= 6000 and budget == "High": selected = COLLEGE_DB["PESU"]
    elif kcet <= 8500 and budget != "Low": selected = COLLEGE_DB["MSRIT"]
    elif kcet <= 15000 and budget != "Low": selected = COLLEGE_DB["BMSCE"]
    elif kcet <= 75000 and budget != "Low": selected = COLLEGE_DB["SJCIT"]
    else: selected = COLLEGE_DB["GOVT"]

    return kcet, jee, chance, status, col, selected

# --- MODERN BOOTSTRAP UI HOUSING TIER ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Admission Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bs-body-bg); }
        .chat-box { height: 480px; overflow-y: auto; background-color: rgba(15, 23, 42, 0.4); border: 1px solid var(--bs-border-color); border-radius: 12px; }
        .bubble { max-width: 80%; padding: 12px 16px; border-radius: 16px; margin-bottom: 15px; position: relative; animation: fadeIn 0.3s ease-in-out; }
        .bubble.user { background-color: #2563EB; color: white; margin-left: auto; border-bottom-right-radius: 4px; }
        .bubble.bot { background-color: #1E293B; color: var(--bs-body-color); margin-right: auto; border-bottom-left-radius: 4px; border: 1px solid var(--bs-border-color); }
        .typing-indicator span { height: 8px; width: 8px; background-color: #94A3B8; display: inline-block; border-radius: 50%; animation: bounce 1.3s infinite ease-in-out; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.15s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.3s; }
        .college-avatar { width: 50px; height: 50px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 11px; text-align: center; }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="p-3 p-md-4">
    <div class="container-fluid max-width-xl mx-auto">
        <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom">
            <h4 class="fw-bold mb-0">🎓 State Allocation & Career Roadmap Portal</h4>
            <button class="btn btn-outline-secondary btn-sm" id="themeToggle">Toggle Dark/Light Mode</button>
        </div>

        <div class="row g-4">
            <div class="col-lg-4">
                <div class="card shadow-sm p-3 mb-3">
                    <h5 class="fw-bold mb-3 text-primary">Student Criteria Profile</h5>
                    <div class="mb-3">
                        <label class="form-label small">FULL NAME PROFILE</label>
                        <input type="text" id="nameInput" class="form-control" value="Kartik">
                    </div>
                    <div class="mb-3">
                        <label class="form-label small">12TH BOARDS PERCENTAGE (%)</label>
                        <input type="number" id="percentageInput" class="form-control" placeholder="e.g. 89.5" step="0.1">
                    </div>
                    <div class="mb-3">
                        <label class="form-label small">TARGET ENGINEERING BRANCH</label>
                        <select id="branchInput" class="form-select">
                            <option value="ECE">Electronics & Communication (ECE)</option>
                            <option value="CSE">Computer Science & Eng (CSE)</option>
                            <option value="MECH">Mechanical Engineering (MECH)</option>
                            <option value="CIVIL">Civil Engineering (CIVIL)</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small">BUDGET ALLOTMENT CAPACITY</label>
                        <select id="budgetInput" class="form-select">
                            <option value="Low">Low Fees (Govt Preference)</option>
                            <option value="Medium" selected>Medium Fees (Merit Scale)</option>
                            <option value="High">High Fees (Premium Infrastructure)</option>
                        </select>
                    </div>
                    <button class="btn btn-success w-100 fw-bold py-2 shadow-sm" id="submitBtn">Compute & Stream Allocation</button>
                </div>

                <div class="card shadow-sm p-3 d-none" id="analyticsCard">
                    <h6 class="fw-bold text-muted mb-2 small">LIVE ADMISSION PROBABILITY METER</h6>
                    <div class="progress mb-2" style="height: 18px;">
                        <div id="chanceBar" class="progress-bar progress-bar-striped progress-bar-animated fw-bold" style="font-size: 11px;">0%</div>
                    </div>
                    <div id="statusLabel" class="small fw-bold text-center text-uppercase">Awaiting Run</div>
                </div>
            </div>

            <div class="col-lg-8">
                <div class="card shadow-sm p-3 d-flex flex-column">
                    <div class="chat-box p-3" id="chatBox">
                        <div class="bubble bot">
                            Hello! Welcome to the Next-Gen Admission Portal. Input your marks layout on the left dock and click <strong>'Compute & Stream Allocation'</strong> to instantly view chat bubbles, rank predictors, campus logos, and generate downloadable report PDFs.
                        </div>
                    </div>
                    <div id="downloadDock" class="mt-3 text-end d-none">
                        <button class="btn btn-outline-primary fw-bold" id="pdfBtn">📂 Download Official Report PDF</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const themeToggle = document.getElementById('themeToggle');
        const submitBtn = document.getElementById('submitBtn');
        const chatBox = document.getElementById('chatBox');
        const analyticsCard = document.getElementById('analyticsCard');
        const pdfBtn = document.getElementById('pdfBtn');

        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            document.documentElement.setAttribute('data-bs-theme', currentTheme === 'dark' ? 'light' : 'dark');
        });

        submitBtn.addEventListener('click', async () => {
            const percentage = document.getElementById('percentageInput').value;
            const name = document.getElementById('nameInput').value;
            const branch = document.getElementById('branchInput').value;
            const budget = document.getElementById('budgetInput').value;

            if(!percentage || percentage < 0 || percentage > 100) {
                alert("Please enter a valid percentage score.");
                return;
            }

            chatBox.innerHTML += `<div class="bubble user">Analyze parameters -> Board Score: ` + percentage + `%, Target Discipline: ` + branch + `</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            const typingId = 'typing_' + Date.now();
            chatBox.innerHTML += `
                <div class="bubble bot d-flex align-items-center" id="` + typingId + `">
                    <span class="me-2 text-muted small" id="loadingText">Bot is analyzing...</span>
                    <div class="typing-indicator"><span></span><span></span><span></span></div>
                </div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ percentage, name, branch, budget })
            });
            const data = await response.json();

            document.getElementById(typingId).remove();

            analyticsCard.classList.remove('d-none');
            const pBar = document.getElementById('chanceBar');
            pBar.style.width = data.chance + '%';
            pBar.className = `progress-bar progress-bar-striped progress-bar-animated fw-bold bg-` + data.col;
            pBar.innerText = data.chance + '%';
            document.getElementById('statusLabel').innerText = data.status;
            document.getElementById('statusLabel').className = `small fw-bold text-center text-` + data.col;

            let botMsg = `
                <div class="fw-bold text-primary mb-2">🎓 CRITERIA ALLOCATION ANALYSIS RECORD</div>
                <div class="row g-2 align-items-center mb-3 bg-body p-2 rounded border border-secondary-subtle">
                    <div class="col-auto">
                        <div class="college-avatar" style="background-color: ` + data.college.logo_bg + `">` + data.college.logo_txt + `</div>
                    </div>
                    <div class="col">
                        <div class="fw-bold text-warning small">🎯 MATCHED TARGET CAMPUS:</div>
                        <div class="fw-bold text-light-emphasis small">` + data.college.name + `</div>
                        <div class="text-muted" style="font-size:12px;">` + data.college.location + ` | Fee: ` + data.college.fee + `</div>
                    </div>
                </div>
                <div class="mb-2 small">
                    Rank Prediction:<br>
                    • Extrapolated KCET Rank: <strong>#` + data.kcet_rank + `</strong><br>
                    • Predicted JEE Core Threshold: <strong>` + data.jee_percentile + ` Percentile</strong>
                </div>
                <div class="p-2 rounded bg-dark border border-secondary text-light small mb-2">
                    <strong>Campus Highlight:</strong> ` + data.college.highlight + `
                </div>
                <div class="small">
                    <div class="fw-bold text-success">⚙️ 4-YEAR SCHOLASTIC PLAN FOR ` + branch + `:</div>
                    ` + data.roadmap + `
                </div>
            `;
            chatBox.innerHTML += `<div class="bubble bot">` + botMsg + `</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            document.getElementById('downloadDock').classList.remove('d-none');
        });

        pdfBtn.addEventListener('click', () => {
            const percentage = document.getElementById('percentageInput').value;
            const name = document.getElementById('nameInput').value;
            const branch = document.getElementById('branchInput').value;
            const budget = document.getElementById('budgetInput').value;
            window.location.href = `/api/download_pdf?name=` + encodeURIComponent(name) + `&percentage=` + percentage + `&branch=` + branch + `&budget=` + budget;
        });
    </script>
</body>
</html>
"""

# --- WEB APP ENDPOINT API CONTROLLERS ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    req_data = request.get_json()
    p = float(req_data.get('percentage', 0))
    b = req_data.get('budget', 'Medium')
    name = req_data.get('name', 'Student')
    br = req_data.get('branch', 'ECE')
    
    kcet, jee, chance, status, col, college = process_analytics(p, b, br)
    
    if br == "ECE":
        roadmap = "Master logic configurations & circuit analytics in years 1-2. Specialize deeply in VLSI hardware and Verilog script designs to clear core hardware test loops at tech hubs like NVIDIA."
    elif br == "CSE":
        roadmap = "Prioritize solid data structures (DSA) and algorithm architectures in years 1-2. Implement scalable full-stack applications and AI/ML deployments to match tier-1 software hiring tracks."
    elif br == "MECH":
        roadmap = "Learn mechanical systems theory and classic CAD drafting blueprints in years 1-2. Transition structural layouts to focus heavily onto EV powertrain arrays and multi-axis assembly robots."
    else:
        roadmap = "Study foundational structural analysis and surveying arrays in years 1-2. Target high-value eco-friendly city planning pipelines and infrastructure appraisal project portfolios."

    return jsonify({
        "kcet_rank": kcet, "jee_percentile": jee, "chance": chance,
        "status": status, "col": col, "college": college, "roadmap": roadmap
    })

@app.route('/api/download_pdf')
def download_pdf():
    name = request.args.get('name', 'Student')
    p = float(request.args.get('percentage', 0))
    br = request.args.get('branch', 'ECE')
    b = request.args.get('budget', 'Medium')
    
    kcet, jee, chance, status, col, college = process_analytics(p, b, br)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#1E3A8A"), spaceAfter=15)
    section_title = ParagraphStyle('SecTitle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#0F172A"), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8)
    
    story.append(Paragraph("OFFICIAL COUNSELING ALLOCATION STATEMENT", title_style))
    story.append(Spacer(1, 10))
    
    data = [
        [Paragraph("<b>Candidate Name:</b>", body_style), Paragraph(name, body_style)],
        [Paragraph("<b>12th Board Score:</b>", body_style), Paragraph(f"{p}%", body_style)],
        [Paragraph("<b>Calculated KCET Rank:</b>", body_style), Paragraph(f"#{kcet}", body_style)],
        [Paragraph("<b>Predicted JEE Percentile:</b>", body_style), Paragraph(f"{jee}%", body_style)]
    ]
    t = Table(data, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("ALLOCATED INSTITUTION PREFERENCE MATCH", section_title))
    story.append(Paragraph(f"<b>Campus Name:</b> {college['name']}", body_style))
    story.append(Paragraph(f"<b>Location Details:</b> {college['location']}", body_style))
    story.append(Paragraph(f"<b>Cost Metric Bracket:</b> {college['fee']}", body_style))
    story.append(Paragraph(f"<b>Core Asset Profile:</b> {college['highlight']}", body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(f"STRATEGIC ENGINEERING ADVISORY LONG-TERM PLAN ({br})", section_title))
    if br == "ECE":
        story.append(Paragraph("Phase 1 (Semesters 1-4): Prioritize solid Boolean structures, microelectronic loops, and Verilog descriptions.", body_style))
        story.append(Paragraph("Phase 2 (Semesters 5-8): Construct physical VLSI layouts and embedded microcontroller software nodes. Directly aligns with premium hardware core vacancies at elite entities like NVIDIA.", body_style))
    elif br == "CSE":
        story.append(Paragraph("Phase 1 (Semesters 1-4): Focus intensely on core Data Structures (DSA), compiler runtimes, and Object Logic.", body_style))
        story.append(Paragraph("Phase 2 (Semesters 5-8): Master high-scale full stack cloud deployments and robust tensor execution models for production clusters.", body_style))
    else:
        story.append(Paragraph("Phase 1-4: Study fundamental discipline mathematics and branch criteria. Build operational portfolio models tracking design constraints to match core company placement pipelines.", body_style))

    doc.build(story)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"{name}_Admission_Report.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 MASTER WEB PLATFORM IS RUNNING NOW!")
    print("👉 OPEN YOUR INTERNET BROWSER AND GO TO: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0')