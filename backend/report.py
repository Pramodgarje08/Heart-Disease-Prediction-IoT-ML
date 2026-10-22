from pathlib import Path
import joblib

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


# ============================================================
# PATH
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = ROOT / "models" / "model_results.joblib"


# ============================================================
# PAGE HEADER / FOOTER
# ============================================================

def add_page_number(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 8)

    canvas.drawString(
        15 * mm,
        10 * mm,
        "Heart Disease Prediction System"
    )

    canvas.drawRightString(
        195 * mm,
        10 * mm,
        f"Page {doc.page}"
    )

    canvas.restoreState()


# ============================================================
# GENERATE REPORT
# ============================================================

def generate_report(patient, history, output_path):

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # PDF DOCUMENT
    # --------------------------------------------------------

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=13
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=11
    )

    story = []

    # ========================================================
    # TITLE
    # ========================================================

    story.append(
        Paragraph(
            "HEART DISEASE PREDICTION SYSTEM",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Patient Health Monitoring & ML Prediction Report",
            subtitle_style
        )
    )

    story.append(
        Table(
            [["PATIENT HEALTH REPORT"]],
            colWidths=[180 * mm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1f4e78")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ])
        )
    )

    story.append(Spacer(1, 12))

    # ========================================================
    # PATIENT DETAILS
    # ========================================================

    story.append(
        Paragraph(
            "1. Patient Information",
            heading_style
        )
    )

    patient_table = [
        ["Patient ID", str(patient.get("patient_id", "-"))],
        ["Name", str(patient.get("name", "-"))],
        ["Age", str(patient.get("age", "-"))],
        ["Gender", str(patient.get("gender", "-"))],
        ["Blood Group", str(patient.get("blood_group") or "-")],
        ["Phone", str(patient.get("phone") or "-")]
    ]

    t1 = Table(
        patient_table,
        colWidths=[45 * mm, 135 * mm]
    )

    t1.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eaf2f8")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(t1)

    # ========================================================
    # LATEST RESULT
    # ========================================================

    story.append(
        Paragraph(
            "2. Latest Health Assessment",
            heading_style
        )
    )

    if history:

        record = history[0]

        age_at_test = record.get(
            "age_at_test",
            "-"
        )

        heart_rate = float(
            record.get("heart_rate") or 0
        )

        spo2 = float(
            record.get("spo2") or 0
        )

        ecg = record.get(
            "ecg",
            "-"
        )

        prediction = record.get(
            "prediction"
        ) or "-"

        risk_level = record.get(
            "risk_level"
        ) or "-"

        confidence = float(
            record.get("confidence") or 0
        )

        timestamp = record.get(
            "timestamp",
            "-"
        )

        latest = [
            ["Parameter", "Measured Result"],
            ["Age at Test", str(age_at_test)],
            ["Heart Rate", f"{heart_rate:.1f} BPM"],
            ["SpO2", f"{spo2:.1f} %"],
            ["ECG Sample", str(ecg)],
            ["Prediction", str(prediction)],
            ["Risk Level", str(risk_level)],
            ["Confidence", f"{confidence * 100:.1f}%"],
            ["Assessment Time", str(timestamp)]
        ]

        t2 = Table(
            latest,
            colWidths=[55 * mm, 125 * mm]
        )

        t2.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BACKGROUND",
             (0, 0),
             (-1, 0),
             colors.HexColor("#1f4e78")),

            ("TEXTCOLOR",
             (0, 0),
             (-1, 0),
             colors.white),

            ("FONTNAME",
             (0, 0),
             (-1, 0),
             "Helvetica-Bold"),

            ("FONTNAME",
             (0, 1),
             (0, -1),
             "Helvetica-Bold"),

            ("BACKGROUND",
             (0, 1),
             (0, -1),
             colors.HexColor("#eaf2f8")),

            ("FONTSIZE",
             (0, 0),
             (-1, -1),
             9),

            ("TOPPADDING",
             (0, 0),
             (-1, -1),
             7),

            ("BOTTOMPADDING",
             (0, 0),
             (-1, -1),
             7),
        ]))

        story.append(t2)

    else:

        story.append(
            Paragraph(
                "No sensor history available.",
                normal_style
            )
        )

    # ========================================================
    # ML MODEL PERFORMANCE
    # ========================================================

    story.append(
        Paragraph(
            "3. Machine Learning Model Performance",
            heading_style
        )
    )

    model_table = [
        ["Metric", "Random Forest"],
    ]

    try:

        results = joblib.load(MODEL_FILE)

        rf = results.get(
            "Random Forest"
        )

        if rf:

            model_table.extend([
                [
                    "Accuracy",
                    f"{rf['accuracy']:.2f}%"
                ],
                [
                    "Precision",
                    f"{rf['precision']:.2f}%"
                ],
                [
                    "Recall",
                    f"{rf['recall']:.2f}%"
                ],
                [
                    "F1 Score",
                    f"{rf['f1']:.2f}%"
                ]
            ])

    except Exception:

        model_table.extend([
            ["Accuracy", "Available from model"],
            ["Precision", "Available from model"],
            ["Recall", "Available from model"],
            ["F1 Score", "Available from model"]
        ])

    t3 = Table(
        model_table,
        colWidths=[90 * mm, 90 * mm]
    )

    t3.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("BACKGROUND",
         (0, 0),
         (-1, 0),
         colors.HexColor("#1f4e78")),

        ("TEXTCOLOR",
         (0, 0),
         (-1, 0),
         colors.white),

        ("FONTNAME",
         (0, 0),
         (-1, 0),
         "Helvetica-Bold"),

        ("FONTNAME",
         (0, 1),
         (0, -1),
         "Helvetica-Bold"),

        ("BACKGROUND",
         (0, 1),
         (0, -1),
         colors.HexColor("#eaf2f8")),

        ("ALIGN",
         (1, 1),
         (1, -1),
         "CENTER"),

        ("FONTSIZE",
         (0, 0),
         (-1, -1),
         9),

        ("TOPPADDING",
         (0, 0),
         (-1, -1),
         7),

        ("BOTTOMPADDING",
         (0, 0),
         (-1, -1),
         7),
    ]))

    story.append(t3)

    # ========================================================
    # HISTORY
    # ========================================================

    story.append(
        Paragraph(
            "4. Recent Patient Monitoring History",
            heading_style
        )
    )

    rows = [
        [
            "Date",
            "Age",
            "HR",
            "SpO2",
            "ECG",
            "Risk"
        ]
    ]

    for record in history[:20]:

        timestamp = record.get(
            "timestamp",
            "-"
        )

        age = record.get(
            "age_at_test",
            "-"
        )

        heart_rate = float(
            record.get("heart_rate") or 0
        )

        spo2 = float(
            record.get("spo2") or 0
        )

        ecg = record.get(
            "ecg",
            "-"
        )

        risk = record.get(
            "risk_level"
        ) or "-"

        rows.append([
            str(timestamp),
            str(age),
            f"{heart_rate:.0f}",
            f"{spo2:.0f}",
            str(ecg),
            str(risk)
        ])

    history_table = Table(
        rows,
        repeatRows=1,
        colWidths=[
            45 * mm,
            20 * mm,
            25 * mm,
            25 * mm,
            35 * mm,
            30 * mm
        ]
    )

    history_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        ("BACKGROUND",
         (0, 0),
         (-1, 0),
         colors.HexColor("#1f4e78")),

        ("TEXTCOLOR",
         (0, 0),
         (-1, 0),
         colors.white),

        ("FONTNAME",
         (0, 0),
         (-1, 0),
         "Helvetica-Bold"),

        ("FONTSIZE",
         (0, 0),
         (-1, -1),
         7),

        ("ALIGN",
         (1, 1),
         (-1, -1),
         "CENTER"),

        ("VALIGN",
         (0, 0),
         (-1, -1),
         "MIDDLE"),

        ("TOPPADDING",
         (0, 0),
         (-1, -1),
         5),

        ("BOTTOMPADDING",
         (0, 0),
         (-1, -1),
         5),
    ]))

    story.append(history_table)

    # ========================================================
    # DOCTOR REMARKS
    # ========================================================

    story.append(
        Paragraph(
            "5. Doctor / Examiner Remarks",
            heading_style
        )
    )

    remarks = Table(
        [
            [
                "Remarks:\n\n"
                "____________________________________________________\n\n"
                "____________________________________________________\n\n"
                "____________________________________________________"
            ]
        ],
        colWidths=[180 * mm],
        rowHeights=[45 * mm]
    )

    remarks.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(remarks)

    story.append(Spacer(1, 12))

    # ========================================================
    # DISCLAIMER
    # ========================================================

    disclaimer = Table(
        [[
            Paragraph(
                "<b>Important:</b> This report is generated by "
                "an academic Heart Disease Prediction System "
                "for project demonstration. The prediction, "
                "risk level and confidence score should not "
                "be considered a medical diagnosis.",
                small_style
            )
        ]],
        colWidths=[180 * mm]
    )

    disclaimer.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(disclaimer)

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    # ========================================================
    # VERIFY
    # ========================================================

    if not output_path.exists():
        raise FileNotFoundError(
            f"PDF was not created: {output_path}"
        )

    return str(output_path)