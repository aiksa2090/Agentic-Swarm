DARK_QSS = """
QWidget {
    background-color: #0b141a;
    color: #e9edef;
    font-family: 'Segoe UI', 'Cairo', Tahoma, sans-serif;
    font-size: 14px;
    selection-background-color: #00a884;
    selection-color: #111b21;
}

/* Navbar */
#Navbar {
    background-color: #111b21;
    border-bottom: 1px solid #202c33;
    padding: 5px;
}

/* Panels */
#LeftPanel, #CenterPanel, #RightPanel {
    background-color: #0b141a;
    border: 1px solid #202c33;
}

#PanelTitle {
    font-weight: bold;
    font-size: 16px;
    color: #00a884;
    padding: 10px;
    background-color: #111b21;
    border-bottom: 1px solid #202c33;
}

/* Navbar Buttons - Professional Colors */
.NavBtn {
    border-radius: 15px;
    padding: 8px 15px;
    font-weight: bold;
    font-size: 13px;
    color: white;
}

#BtnStart { background-color: #00a884; color: #111b21; }
#BtnStart:hover { background-color: #06cf9c; }

#BtnPause { background-color: #eab308; color: #111b21; }
#BtnStop { background-color: #ef4444; }
#BtnRestart { background-color: #8b5cf6; } /* Purple */
#BtnExport { background-color: #f97316; } /* Orange */
#BtnContinue { background-color: #3b82f6; } /* Blue */
#BtnModels { background-color: #6366f1; }
#BtnDiagnosis { background-color: #ec4899; } /* Pink */

#AutoScrollBtn {
    background-color: #202c33;
    border: 1px solid #00a884;
    color: #00a884;
    padding: 5px 15px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: bold;
}
#AutoScrollBtn[active="true"] {
    background-color: #00a884;
    color: #111b21;
}

/* Agent Cards */
#AgentCard {
    background-color: #111b21;
    border: 1px solid #202c33;
    border-radius: 10px;
    margin: 5px;
    padding: 10px;
}
#AgentCardTitle {
    color: #e9edef;
    font-weight: bold;
    font-size: 14px;
}
#AgentCardModel {
    color: #3b82f6;
    font-size: 11px;
}
#AgentStatusLabel {
    color: #8696a0;
    font-size: 12px;
}

#DetailsBtn {
    background-color: transparent;
    color: #3b82f6;
    border: 1px solid #3b82f6;
    border-radius: 4px;
    padding: 2px 10px;
    font-size: 12px;
}
#DetailsBtn:hover {
    background-color: #3b82f6;
    color: white;
}

/* Chat & Draft Boxes */
QTextBrowser {
    background-color: #0b141a;
    border: none;
    padding: 15px;
    line-height: 1.6;
}

/* Input Area */
#InputFrame {
    background-color: #111b21;
    border-top: 1px solid #202c33;
    padding: 10px;
}

#MainInput {
    background-color: #2a3942;
    border-radius: 10px;
    padding: 10px 15px;
    color: #e9edef;
    border: 1px solid #202c33;
}

#MainInput:focus {
    border: 1px solid #00a884;
}

/* Custom Containers in Dialogs */
.AgentEditBox {
    background-color: #111b21;
    border: 2px solid #00a884;
    border-radius: 12px;
    margin: 10px;
    padding: 20px;
}

#AgentBucketTitle {
    color: #00a884;
    font-size: 16px;
    font-weight: bold;
    border-bottom: 1px solid #202c33;
    padding-bottom: 8px;
    margin-bottom: 15px;
}

.AgentEditBox QLabel {
    color: #e9edef;
    font-weight: bold;
    margin-bottom: 5px;
}

.AgentEditBox QComboBox, .AgentEditBox QTextEdit {
    background-color: #2a3942;
    border: 2px solid #3b4a54;
    border-radius: 8px;
    padding: 10px;
    color: #ffffff;
    font-size: 14px;
}

.AgentEditBox QComboBox:focus, .AgentEditBox QTextEdit:focus {
    border: 2px solid #00a884;
    background-color: #323739;
}

.AgentEditBox QComboBox:focus, .AgentEditBox QTextEdit:focus {
    border: 1px solid #00a884;
    background-color: #2a3942;
}

#SendBtn {
    background-color: #00a884;
    border-radius: 20px;
    width: 40px;
    height: 40px;
}

/* Scrollbars - Slim Modern */
QScrollBar:vertical {
    border: none;
    background: #0b141a;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #374151;
    border-radius: 4px;
}

/* Splitter */
QSplitter::handle {
    background-color: #202c33;
}
"""
