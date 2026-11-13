import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/observer-report";

function App() {
  const [content, setContent] = useState("");
  const [userQuery, setUserQuery] = useState("");
  const [comparisonGoal, setComparisonGoal] = useState("");

  const [report, setReport] = useState(null);
  const [comparison, setComparison] = useState(null);

  const [loading, setLoading] = useState(false);
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [error, setError] = useState("");
  const [comparisonError, setComparisonError] = useState("");

  // ==========================================
  // COMMON API FUNCTION
  // ==========================================

  async function fetchObserverReport(query) {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content,
        user_query: query,
      }),
    });

    if (!response.ok) {
      const details = await response.text();
      throw new Error(
        `Request failed (${response.status}): ${details}`
      );
    }

    return await response.json();
  }

  // ==========================================
  // TEXT FORMATTING
  // ==========================================

  function formatText(value) {
    if (!value) return "Not available";

    return value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  function getImportanceClass(value) {
    const importance = (value || "").toLowerCase();

    if (importance === "high") return "importance-high";
    if (importance === "medium") return "importance-medium";

    return "importance-low";
  }

  function getPriorityClass(value) {
    const priority = (value || "medium").toLowerCase();

    if (priority === "high") return "priority-high";
    if (priority === "medium") return "priority-medium";

    return "priority-low";
  }

  // ==========================================
  // NORMAL ANALYSIS
  // ==========================================

  async function analyzeContent() {
    if (!content.trim() || !userQuery.trim()) {
      setError(
        "Please enter both the content and your analytical goal."
      );
      return;
    }

    setLoading(true);
    setError("");
    setReport(null);
    setComparison(null);
    setComparisonError("");

    try {
      const data = await fetchObserverReport(userQuery);
      setReport(data);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the backend. Check that FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  // ==========================================
  // FINDING NORMALIZATION
  // ==========================================

  function normalizeObservation(observation) {
    return (observation || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ");
  }

  // ==========================================
  // OBSERVER COMPARISON
  // ==========================================

  function buildComparison(reportA, reportB) {
    const findingsA = reportA.findings || [];
    const findingsB = reportB.findings || [];

    const observationsA = new Map();
    const observationsB = new Map();

    findingsA.forEach((finding) => {
      const key = normalizeObservation(finding.observation);

      if (key && !observationsA.has(key)) {
        observationsA.set(key, finding);
      }
    });

    findingsB.forEach((finding) => {
      const key = normalizeObservation(finding.observation);

      if (key && !observationsB.has(key)) {
        observationsB.set(key, finding);
      }
    });

    const sharedObservations = [];
    const uniqueToA = [];
    const uniqueToB = [];

    observationsA.forEach((finding, key) => {
      if (observationsB.has(key)) {
        sharedObservations.push({
          observation: finding.observation,
          findingA: finding,
          findingB: observationsB.get(key),
        });
      } else {
        uniqueToA.push(finding);
      }
    });

    observationsB.forEach((finding, key) => {
      if (!observationsA.has(key)) {
        uniqueToB.push(finding);
      }
    });

    return {
      reportA,
      reportB,
      sharedObservations,
      uniqueToA,
      uniqueToB,
    };
  }

  async function compareObservers() {
    if (
      !content.trim() ||
      !userQuery.trim() ||
      !comparisonGoal.trim()
    ) {
      setComparisonError(
        "Please enter the content and both observer goals."
      );
      return;
    }

    if (
      userQuery.trim().toLowerCase() ===
      comparisonGoal.trim().toLowerCase()
    ) {
      setComparisonError(
        "Please enter two different analytical goals."
      );
      return;
    }

    setComparisonLoading(true);
    setComparisonError("");
    setComparison(null);

    try {
      const [reportA, reportB] = await Promise.all([
        fetchObserverReport(userQuery),
        fetchObserverReport(comparisonGoal),
      ]);

      setComparison(buildComparison(reportA, reportB));
    } catch (err) {
      setComparisonError(
        err.message ||
          "Could not compare observers. Check that the backend is running."
      );
    } finally {
      setComparisonLoading(false);
    }
  }

  // ==========================================
  // PRIORITY SUMMARY
  // ==========================================

  const priorityCounts = (report?.findings || []).reduce(
    (counts, finding) => {
      const priority = (finding.priority || "medium").toLowerCase();

      if (priority === "high") {
        counts.high++;
      } else if (priority === "low") {
        counts.low++;
      } else {
        counts.medium++;
      }

      return counts;
    },
    { high: 0, medium: 0, low: 0 }
  );

  const totalPriorityFindings =
    priorityCounts.high +
    priorityCounts.medium +
    priorityCounts.low;

  // ==========================================
  // AGENT CONTRIBUTION
  // ==========================================

  const agentContributions = Object.entries(
    report?.agent_summary || {}
  );

  const totalAgentFindings = agentContributions.reduce(
    (total, [, details]) =>
      total + (details.total_findings || 0),
    0
  );

  const sharedObservationCount = (
    report?.finding_groups || []
  ).filter((group) => group.perspective_count > 1).length;

  const totalPerspectives = (
    report?.finding_groups || []
  ).reduce(
    (total, group) => total + (group.perspective_count || 0),
    0
  );

  // ==========================================
  // REUSABLE FINDING BADGES
  // ==========================================

  function FindingBadges({ finding }) {
    return (
      <div className="finding-badges">
        <span
          className={getImportanceClass(finding.goal_importance)}
        >
          Goal Importance: {formatText(finding.goal_importance)}
        </span>

        <span className={getPriorityClass(finding.priority)}>
          Priority: {formatText(finding.priority || "medium")}
        </span>
      </div>
    );
  }

  // ==========================================
  // REUSABLE COMPARISON COLUMN
  // ==========================================

  function ComparisonColumn({
    title,
    observerReport,
    uniqueFindings,
  }) {
    const isEmpty = uniqueFindings.length === 0;

    return (
      <article
        className={`panel observer-column ${
          isEmpty ? "empty-observer-column" : ""
        }`}
      >
        <h3>{title}</h3>

        <p>
          <strong>Primary Goal:</strong>{" "}
          {formatText(observerReport.primary_goal)}
        </p>

        <p>
          <strong>Selected Agents:</strong>{" "}
          {observerReport.selected_agent_count}
        </p>

        <p>
          <strong>Total Findings:</strong>{" "}
          {observerReport.total_findings}
        </p>

        <p>
          <strong>Finding Groups:</strong>{" "}
          {observerReport.total_finding_groups}
        </p>

        <h4>Selected Specialist Agents</h4>

        <div className="group-metadata">
          {Object.keys(observerReport.agent_summary || {}).length > 0 ? (
            Object.keys(observerReport.agent_summary).map((agent) => (
              <p key={agent}>{formatText(agent)}</p>
            ))
          ) : (
            <p>No specialist agents selected.</p>
          )}
        </div>

        <h4>
          Unique Observations ({uniqueFindings.length})
        </h4>

        {isEmpty ? (
          <p className="empty-observer-message">
            No unique observations for this observer.
          </p>
        ) : (
          uniqueFindings.map((finding, index) => (
            <article className="perspective-card" key={index}>
              <p>{finding.observation}</p>

              <p>
                <strong>Agent:</strong>{" "}
                {formatText(finding.agent)}
              </p>

              <p>
                <strong>Analysis Area:</strong>{" "}
                {(finding.analysis_area || [])
                  .map(formatText)
                  .join(", ") || "Not available"}
              </p>

              <FindingBadges finding={finding} />
            </article>
          ))
        )}
      </article>
    );
  }

  // ==========================================
  // EXPORT COMPARISON REPORT AS PDF
  // ==========================================

  function exportComparisonPDF() {
    const reportElement = document.getElementById("comparison-report");

    if (!reportElement || !comparison) {
      setComparisonError(
        "Please generate an observer comparison before exporting."
      );
      return;
    }

    const printWindow = window.open("", "_blank");

    if (!printWindow) {
      setComparisonError(
        "Please allow pop-ups in your browser to export the PDF."
      );
      return;
    }

    // Work on a copy so the visible dashboard is never changed.
    const clonedReport = reportElement.cloneNode(true);

    // Remove controls that should not appear in the exported report.
    clonedReport.querySelectorAll("button").forEach((button) => {
      button.remove();
    });

    const reportHeading = clonedReport.querySelector(".report-heading");
    const summaryGrid = clonedReport.querySelector(":scope > .summary-grid");
    const reportPanels = Array.from(
      clonedReport.querySelectorAll(":scope > .panel")
    );

    const agentSelectionPanel = reportPanels[0] || null;
    const sharedPanel = reportPanels[1] || null;
    const observerSpecificPanel = reportPanels[2] || null;
    const conclusionPanel = reportPanels[3] || null;

    if (
      !reportHeading ||
      !summaryGrid ||
      !agentSelectionPanel ||
      !sharedPanel ||
      !observerSpecificPanel ||
      !conclusionPanel
    ) {
      printWindow.close();
      setComparisonError(
        "The comparison report structure was not recognized. Please refresh and try again."
      );
      return;
    }

    // Split shared observations across the first two print pages.
    const sharedCards = Array.from(
      sharedPanel.querySelectorAll(":scope > .observation-group")
    );

    const splitIndex = Math.ceil(sharedCards.length / 2);
    const firstPageSharedCards = sharedCards.slice(0, splitIndex);
    const secondPageSharedCards = sharedCards.slice(splitIndex);

    function createPage(className) {
      const page = document.createElement("section");
      page.className = `pdf-page ${className}`;
      return page;
    }

    function addSharedSection(page, cards, continued = false) {
      const section = document.createElement("section");
      section.className = "panel pdf-shared-section";

      const heading = document.createElement("h3");
      heading.textContent = continued
        ? "Shared Observations (continued)"
        : sharedPanel.querySelector("h3")?.textContent ||
          "Shared Observations";
      section.appendChild(heading);

      const description = document.createElement("p");
      description.className = "priority-description";
      description.textContent =
        sharedPanel.querySelector(".priority-description")?.textContent ||
        "Exact observations identified by both observers.";
      section.appendChild(description);

      if (cards.length > 0) {
        cards.forEach((card) => {
          section.appendChild(card.cloneNode(true));
        });
      } else {
        const emptyMessage = document.createElement("p");
        emptyMessage.textContent =
          "No additional shared observations on this page.";
        section.appendChild(emptyMessage);
      }

      page.appendChild(section);
    }

    // PAGE 1: Overview, agent selection, and first shared observations.
    const page1 = createPage("pdf-page-one");
    page1.appendChild(reportHeading.cloneNode(true));
    page1.appendChild(summaryGrid.cloneNode(true));
    page1.appendChild(agentSelectionPanel.cloneNode(true));
    addSharedSection(page1, firstPageSharedCards, false);

    // PAGE 2: Remaining shared observations.
    const page2 = createPage("pdf-page-two");
    addSharedSection(page2, secondPageSharedCards, true);

    // PAGE 3: Observer-specific observations and comparison summary.
    const page3 = createPage("pdf-page-three");
    page3.appendChild(observerSpecificPanel.cloneNode(true));
    page3.appendChild(conclusionPanel.cloneNode(true));

    const printStyles = `
      * {
        box-sizing: border-box !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }

      html, body {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        background: #ffffff !important;
        color: #1f2937 !important;
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 9pt !important;
        line-height: 1.32 !important;
      }

      body {
        padding: 0 !important;
      }

      .pdf-page {
        width: 100% !important;
        min-height: 277mm !important;
        padding: 0 !important;
        margin: 0 !important;
        background: #ffffff !important;
        break-after: page !important;
        page-break-after: always !important;
      }

      .pdf-page:last-child {
        break-after: auto !important;
        page-break-after: auto !important;
      }

      .pdf-page > * {
        width: 100% !important;
        max-width: 100% !important;
      }

      .pdf-page * {
        color: #1f2937 !important;
        box-shadow: none !important;
        text-shadow: none !important;
      }

      h1, h2, h3, h4, h5 {
        color: #111827 !important;
        line-height: 1.25 !important;
        margin-top: 4px !important;
        margin-bottom: 5px !important;
      }

      p {
        color: #374151 !important;
        overflow-wrap: anywhere !important;
        margin-top: 3px !important;
        margin-bottom: 4px !important;
      }

      .eyebrow {
        color: #2563eb !important;
        font-size: 8pt !important;
        font-weight: bold !important;
        letter-spacing: 1px !important;
      }

      .report-heading {
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
        gap: 10px !important;
        margin-bottom: 8px !important;
        padding-bottom: 7px !important;
        border-bottom: 2px solid #dbeafe !important;
      }

      .summary-grid {
        display: grid !important;
        grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
        gap: 7px !important;
        margin-bottom: 8px !important;
      }

      .panel, .summary-card, .observation-group, .perspective-card {
        background: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
        padding: 8px !important;
        margin-bottom: 7px !important;
      }

      .summary-card {
        break-inside: avoid !important;
        page-break-inside: avoid !important;
      }

      .observation-group {
        break-inside: avoid !important;
        page-break-inside: avoid !important;
        padding: 8px !important;
        margin-bottom: 7px !important;
      }

      .group-observation {
        color: #111827 !important;
        font-size: 9.5pt !important;
      }

      .perspective-card {
        padding: 6px !important;
        margin-bottom: 5px !important;
      }

      .perspective-card p {
        font-size: 8pt !important;
        line-height: 1.25 !important;
        margin: 2px 0 !important;
      }

      .perspective-card strong {
        color: #1d4ed8 !important;
      }

      .finding-badges {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 4px !important;
        margin: 4px 0 !important;
      }

      .importance-high, .importance-medium, .importance-low,
      .priority-high, .priority-medium, .priority-low {
        display: inline-block !important;
        padding: 3px 6px !important;
        border-radius: 20px !important;
        font-size: 7.5pt !important;
        font-weight: bold !important;
      }

      .importance-high {
        background: #dbeafe !important;
        color: #1d4ed8 !important;
      }

      .importance-medium {
        background: #fef3c7 !important;
        color: #92400e !important;
      }

      .importance-low {
        background: #e5e7eb !important;
        color: #374151 !important;
      }

      .priority-high {
        background: #fee2e2 !important;
        color: #b91c1c !important;
      }

      .priority-medium {
        background: #ffedd5 !important;
        color: #9a3412 !important;
      }

      .priority-low {
        background: #dcfce7 !important;
        color: #166534 !important;
      }

      .goal-badge {
        background: #dbeafe !important;
        color: #1d4ed8 !important;
        padding: 4px 7px !important;
        border-radius: 6px !important;
      }

      .pdf-shared-section {
        padding: 8px !important;
        margin-bottom: 0 !important;
      }

      .pdf-shared-section > h3 {
        margin-top: 0 !important;
      }

      .observer-specific-section {
        padding: 8px !important;
        margin: 0 0 8px 0 !important;
        break-inside: auto !important;
        page-break-inside: auto !important;
      }

      .observer-specific-section > h3,
      .observer-specific-section > p {
        margin-top: 3px !important;
        margin-bottom: 4px !important;
      }

      .observer-specific-grid {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 8px !important;
      }

      .observer-specific-grid.single-unique-column {
        grid-template-columns: 1fr !important;
      }

      .observer-column {
        padding: 7px !important;
        margin-bottom: 4px !important;
      }

      .observer-column h3,
      .observer-column h4 {
        margin: 3px 0 !important;
      }

      .observer-column p {
        font-size: 8pt !important;
        line-height: 1.25 !important;
        margin: 2px 0 !important;
      }

      .empty-observer-column {
        min-height: auto !important;
        padding: 8px !important;
      }

      .empty-observer-message {
        margin: 4px 0 !important;
      }

      .observer-specific-grid.single-unique-column
      .observer-column:not(.empty-observer-column) {
        width: 100% !important;
      }

      .pdf-page-three > .panel:last-child {
        padding: 8px !important;
        margin-top: 5px !important;
        margin-bottom: 0 !important;
        break-inside: avoid !important;
        page-break-inside: avoid !important;
      }

      .pdf-page-three > .panel:last-child p {
        font-size: 8.5pt !important;
        line-height: 1.25 !important;
        margin: 3px 0 !important;
      }

      .priority-description, .priority-note {
        color: #4b5563 !important;
        font-size: 8pt !important;
      }

      button {
        display: none !important;
      }

      @page {
        size: A4;
        margin: 10mm;
      }

      @media print {
        html, body {
          background: #ffffff !important;
        }

        .pdf-page {
          min-height: 277mm !important;
        }
      }
    `;

    printWindow.document.open();
    printWindow.document.write(`
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>ODRE Observer Comparison Report</title>
          <style>${printStyles}</style>
        </head>
        <body>
          ${page1.outerHTML}
          ${page2.outerHTML}
          ${page3.outerHTML}

          <script>
            window.onload = function () {
              setTimeout(function () {
                window.focus();
                window.print();
              }, 700);
            };
          <\/script>
        </body>
      </html>
    `);

    printWindow.document.close();
    setComparisonError("");
  }
    // ==========================================
  // MAIN UI
  // ==========================================

  return (
    <main className="app">

      {/* HEADER */}

      <header className="hero">
        <p className="eyebrow">
          ADAPTIVE INTELLIGENCE PLATFORM
        </p>

        <h1>Observer Goal Modeling</h1>

        <p className="subtitle">
          Multi-Agent Adaptive Intelligence System
        </p>

        <p className="description">
          Analyze the same content from different observer
          perspectives using goal detection and specialized AI agents.
        </p>
      </header>

      {/* INPUT SECTION */}

      <section className="panel input-panel">
        <h2>Start Your Analysis</h2>

        <label htmlFor="content">
          Content to analyze
        </label>

        <textarea
          id="content"
          rows={6}
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="Paste website content or other text here..."
        />

        <label htmlFor="goal">
          Your analytical goal
        </label>

        <input
          id="goal"
          type="text"
          value={userQuery}
          onChange={(event) => setUserQuery(event.target.value)}
          placeholder="e.g. Analyze security risks and business revenue"
        />

        <button onClick={analyzeContent} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Content"}
        </button>

        {error && <p className="error">{error}</p>}

        <hr />

        {/* OBSERVER COMPARISON INPUT */}

        <div className="comparison-input">
          <p className="eyebrow">NEW FEATURE</p>

          <h3>Compare Two Observer Perspectives</h3>

          <p className="priority-description">
            Keep the same content and compare two different
            analytical goals.
          </p>

          <label htmlFor="comparisonGoal">
            Second observer's analytical goal
          </label>

          <input
            id="comparisonGoal"
            type="text"
            value={comparisonGoal}
            onChange={(event) =>
              setComparisonGoal(event.target.value)
            }
            placeholder="e.g. Analyze this application from a business perspective"
          />

          <button
            onClick={compareObservers}
            disabled={comparisonLoading}
          >
            {comparisonLoading
              ? "Comparing Observers..."
              : "Compare Observers"}
          </button>

          {comparisonError && (
            <p className="error">{comparisonError}</p>
          )}
        </div>
      </section>

      {/* ==========================================
          NORMAL OBSERVER REPORT
      ========================================== */}

      {report && (
        <section className="report-section">

          <div className="report-heading">
            <div>
              <p className="eyebrow">ANALYSIS RESULTS</p>
              <h2>Observer-Specific Report</h2>
            </div>

            <span className="goal-badge">
              {formatText(report.primary_goal)}
            </span>
          </div>

          {/* SUMMARY CARDS */}

          <div className="summary-grid">

            <article className="summary-card">
              <p>Primary Goal</p>
              <h3>{formatText(report.primary_goal)}</h3>
            </article>

            <article className="summary-card">
              <p>Selected Agents</p>
              <h3>{report.selected_agent_count}</h3>
            </article>

            <article className="summary-card">
              <p>Total Findings</p>
              <h3>{report.total_findings}</h3>
            </article>

            <article className="summary-card">
              <p>Finding Groups</p>
              <h3>{report.total_finding_groups}</h3>
            </article>

          </div>

          {/* ======================================
              PRIORITY SUMMARY DASHBOARD
          ====================================== */}

          <section className="priority-dashboard">

            <div className="priority-dashboard-heading">
              <div>
                <p className="eyebrow">FINDING ANALYTICS</p>
                <h3>Priority Summary</h3>

                <p className="priority-description">
                  Distribution of preliminary review priorities
                  across all specialist findings.
                </p>
              </div>

              <span className="priority-total">
                {totalPriorityFindings} Findings
              </span>
            </div>

            <div className="priority-summary-grid">

              <article className="priority-summary-card high-card">
                <p>High Priority</p>
                <h2>{priorityCounts.high}</h2>
                <span>
                  {totalPriorityFindings
                    ? (
                        (priorityCounts.high /
                          totalPriorityFindings) *
                        100
                      ).toFixed(1)
                    : "0.0"}
                  %
                </span>
              </article>

              <article className="priority-summary-card medium-card">
                <p>Medium Priority</p>
                <h2>{priorityCounts.medium}</h2>
                <span>
                  {totalPriorityFindings
                    ? (
                        (priorityCounts.medium /
                          totalPriorityFindings) *
                        100
                      ).toFixed(1)
                    : "0.0"}
                  %
                </span>
              </article>

              <article className="priority-summary-card low-card">
                <p>Low Priority</p>
                <h2>{priorityCounts.low}</h2>
                <span>
                  {totalPriorityFindings
                    ? (
                        (priorityCounts.low /
                          totalPriorityFindings) *
                        100
                      ).toFixed(1)
                    : "0.0"}
                  %
                </span>
              </article>

            </div>

            {/* PRIORITY DISTRIBUTION */}

            <div className="priority-distribution">
              <h4>Priority Distribution</h4>

              {[
                {
                  label: "High",
                  count: priorityCounts.high,
                  className: "high-bar",
                },
                {
                  label: "Medium",
                  count: priorityCounts.medium,
                  className: "medium-bar",
                },
                {
                  label: "Low",
                  count: priorityCounts.low,
                  className: "low-bar",
                },
              ].map((item) => (
                <div
                  className="priority-bar-item"
                  key={item.label}
                >
                  <div className="priority-bar-label">
                    <span>{item.label}</span>
                    <strong>{item.count}</strong>
                  </div>

                  <div className="priority-bar-track">
                    <div
                      className={`priority-bar-fill ${item.className}`}
                      style={{
                        width: `${
                          totalPriorityFindings
                            ? (item.count /
                                totalPriorityFindings) *
                              100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <p className="priority-note">
              Note: Priority levels are preliminary category-based
              review defaults, not verified severity measurements.
            </p>

          </section>

          {/* ======================================
              AGENT CONTRIBUTION DASHBOARD
          ====================================== */}

          <section className="panel agent-contribution-dashboard">

            <div className="priority-dashboard-heading">
              <div>
                <p className="eyebrow">MULTI-AGENT ANALYTICS</p>
                <h3>Agent Contribution Dashboard</h3>

                <p className="priority-description">
                  Compare the number of findings contributed by each
                  selected specialist agent.
                </p>
              </div>

              <span className="priority-total">
                {agentContributions.length} Agents
              </span>
            </div>

            <div className="summary-grid">

              <article className="summary-card">
                <p>Total Agent Findings</p>
                <h3>{totalAgentFindings}</h3>
              </article>

              <article className="summary-card">
                <p>Shared Observations</p>
                <h3>{sharedObservationCount}</h3>
              </article>

              <article className="summary-card">
                <p>Total Perspectives</p>
                <h3>{totalPerspectives}</h3>
              </article>

            </div>

            <div className="agent-contribution-list">
              <h4>Individual Agent Contributions</h4>

              {agentContributions.length > 0 ? (
                agentContributions.map(([goal, details]) => {
                  const findingCount =
                    details.total_findings || 0;

                  const contributionPercentage =
                    totalAgentFindings > 0
                      ? (findingCount / totalAgentFindings) * 100
                      : 0;

                  return (
                    <div className="weight-item" key={goal}>

                      <div className="weight-label">
                        <span>{formatText(goal)}</span>

                        <strong>
                          {findingCount} Findings (
                          {contributionPercentage.toFixed(1)}%)
                        </strong>
                      </div>

                      <div className="progress-track">
                        <div
                          className="progress-fill"
                          style={{
                            width: `${contributionPercentage}%`,
                          }}
                        />
                      </div>

                    </div>
                  );
                })
              ) : (
                <p>No agent contribution information available.</p>
              )}
            </div>

            <p className="priority-note">
              Note: Contribution percentages represent each agent's
              share of individual findings. The same observation can
              contribute to multiple agents.
            </p>

          </section>

          {/* ======================================
              OBSERVER GOAL DISTRIBUTION
          ====================================== */}

          <section className="panel">
            <h3>Observer Goal Distribution</h3>

            {Object.entries(report.goal_weights || {}).map(
              ([goal, weight]) => (
                <div className="weight-item" key={goal}>

                  <div className="weight-label">
                    <span>{formatText(goal)}</span>
                    <strong>
                      {(weight * 100).toFixed(0)}%
                    </strong>
                  </div>

                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${weight * 100}%`,
                      }}
                    />
                  </div>

                </div>
              )
            )}
          </section>

          {/* ======================================
              INDIVIDUAL AGENT FINDINGS
          ====================================== */}

          <section className="findings-section">

            <h3>Agent Findings</h3>

            {report.findings?.length === 0 ? (
              <p>
                No keyword matches were found for the selected goals.
              </p>
            ) : (
              report.findings.map((finding, index) => (
                <article className="finding" key={index}>

                  <div className="finding-header">

                    <div>
                      <p className="finding-number">
                        FINDING {String(index + 1).padStart(2, "0")}
                      </p>

                      <h4>
                        {formatText(
                          finding.analysis_area?.[0] || finding.goal
                        )}
                      </h4>
                    </div>

                    <FindingBadges finding={finding} />

                  </div>

                  <p className="observation">
                    {finding.observation}
                  </p>

                  <div className="finding-details">

                    <p>
                      <strong>Observer Goal:</strong>{" "}
                      {formatText(finding.goal)}
                    </p>

                    <p>
                      <strong>AI Agent:</strong>{" "}
                      {formatText(finding.agent)}
                    </p>

                    <p>
                      <strong>Goal Weight:</strong>{" "}
                      {((finding.goal_weight ?? 0) * 100).toFixed(0)}%
                    </p>

                    <p>
                      <strong>Analysis Area:</strong>{" "}
                      {(finding.analysis_area || [])
                        .map(formatText)
                        .join(", ") || "Not available"}
                    </p>

                    <p>
                      <strong>Matched Keywords:</strong>{" "}
                      {(finding.matched_keywords || []).join(", ") ||
                        "None"}
                    </p>

                    <p>
                      <strong>Selection Reason:</strong>{" "}
                      {finding.selection_reason || "Not available"}
                    </p>

                  </div>

                  {finding.review_question && (
                    <div className="recommendation-block">
                      <strong>Review Question</strong>
                      <p>{finding.review_question}</p>
                    </div>
                  )}

                  {finding.recommended_check && (
                    <div className="recommendation-block">
                      <strong>Recommended Check</strong>
                      <p>{finding.recommended_check}</p>
                    </div>
                  )}

                  <p className="finding-status">
                    Status: {formatText(finding.status)}
                  </p>

                </article>
              ))
            )}

          </section>

          {/* ======================================
              GROUPED OBSERVATIONS
          ====================================== */}

          <section className="grouped-section">

            <div className="grouped-heading">
              <div>
                <p className="eyebrow">MULTI-AGENT PERSPECTIVES</p>
                <h3>Grouped Observations</h3>

                <p className="grouped-description">
                  Shared observations analyzed from different
                  specialist perspectives.
                </p>
              </div>

              <span className="group-count">
                {report.total_finding_groups || 0} Groups
              </span>
            </div>

            {report.finding_groups?.length > 0 ? (
              report.finding_groups.map((group, groupIndex) => (
                <article
                  className="observation-group"
                  key={group.group_id ?? groupIndex}
                >

                  <div className="group-header">
                    <span className="group-number">
                      GROUP{" "}
                      {String(
                        group.group_id ?? groupIndex + 1
                      ).padStart(2, "0")}
                    </span>

                    <span className="perspective-count">
                      {group.perspective_count ??
                        group.perspectives?.length ??
                        0}{" "}
                      Perspectives
                    </span>
                  </div>

                  <h4 className="group-observation">
                    {group.observation}
                  </h4>

                  <div className="group-metadata">

                    <p>
                      <strong>Specialist Agents:</strong>{" "}
                      {(group.agents || [])
                        .map(formatText)
                        .join(", ")}
                    </p>

                    <p>
                      <strong>Observer Goals:</strong>{" "}
                      {(group.goals || [])
                        .map(formatText)
                        .join(", ")}
                    </p>

                    <p>
                      <strong>Matched Keywords:</strong>{" "}
                      {(group.matched_keywords || []).join(", ") ||
                        "None"}
                    </p>

                  </div>

                  <div className="perspectives-section">
                    <h5>Agent Perspectives</h5>

                    {group.perspectives?.map(
                      (perspective, index) => (
                        <div
                          className="perspective-card"
                          key={`${group.group_id ?? groupIndex}-${index}`}
                        >

                          <div className="perspective-header">
                            <strong>
                              {formatText(perspective.agent)}
                            </strong>

                            <FindingBadges finding={perspective} />
                          </div>

                          <p>
                            <strong>Analysis Area:</strong>{" "}
                            {(perspective.analysis_area || [])
                              .map(formatText)
                              .join(", ") || "Not available"}
                          </p>

                          <p>
                            <strong>Observer Goal:</strong>{" "}
                            {formatText(perspective.goal)}
                          </p>

                          {perspective.review_question && (
                            <p>
                              <strong>Review Question:</strong>{" "}
                              {perspective.review_question}
                            </p>
                          )}

                          {perspective.recommended_check && (
                            <p>
                              <strong>Recommended Check:</strong>{" "}
                              {perspective.recommended_check}
                            </p>
                          )}

                        </div>
                      )
                    )}
                  </div>

                </article>
              ))
            ) : (
              <p>No grouped observations available.</p>
            )}

          </section>

        </section>
      )}
            {/* ==========================================
          OBSERVER COMPARISON DASHBOARD
      ========================================== */}

      {comparison && (
        <section
          id="comparison-report"
          className="report-section comparison-dashboard"
        >

          {/* COMPARISON HEADER */}

          <div className="report-heading">

            <div>
              <p className="eyebrow">
                MULTI-OBSERVER ANALYTICS
              </p>

              <h2>Observer Comparison Dashboard</h2>

              <p className="priority-description">
                Comparison of two observer perspectives using the
                same input content.
              </p>
            </div>

            {/* EXPORT PDF BUTTON */}

            <div className="report-actions">

              <span className="goal-badge">
                Comparison
              </span>

              <button
                type="button"
                className="export-pdf-button"
                onClick={exportComparisonPDF}
                title="Download observer comparison as PDF"
              >
                <span className="export-pdf-icon">
                  ↓
                </span>

                <span>Export PDF</span>
              </button>

            </div>

          </div>

          {/* ======================================
              COMPARISON SUMMARY CARDS
          ====================================== */}

          <div className="summary-grid">

            <article className="summary-card">
              <p>Observer A</p>

              <h3>
                {formatText(comparison.reportA.primary_goal)}
              </h3>
            </article>

            <article className="summary-card">
              <p>Observer B</p>

              <h3>
                {formatText(comparison.reportB.primary_goal)}
              </h3>
            </article>

            <article className="summary-card">
              <p>Shared Observations</p>

              <h3>
                {comparison.sharedObservations.length}
              </h3>
            </article>

            <article className="summary-card">
              <p>Total Unique Observations</p>

              <h3>
                {comparison.uniqueToA.length +
                  comparison.uniqueToB.length}
              </h3>
            </article>

          </div>

          {/* ======================================
              SPECIALIST AGENT SELECTION COMPARISON
          ====================================== */}

          <section className="panel">

            <h3>Specialist Agent Selection Comparison</h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(240px, 1fr))",
                gap: "16px",
              }}
            >

              {[comparison.reportA, comparison.reportB].map(
                (observerReport, index) => (
                  <article
                    className="summary-card"
                    key={index}
                  >

                    <h4>
                      Observer {index === 0 ? "A" : "B"} —{" "}
                      {formatText(observerReport.primary_goal)}
                    </h4>

                    <p>
                      <strong>Selected agents:</strong>{" "}
                      {observerReport.selected_agent_count}
                    </p>

                    {Object.keys(
                      observerReport.agent_summary || {}
                    ).map((agent) => (
                      <p key={agent}>
                        {formatText(agent)} —{" "}
                        {
                          observerReport.agent_summary[agent]
                            .total_findings
                        }
                        {" findings"}
                      </p>
                    ))}

                  </article>
                )
              )}

            </div>

          </section>

          {/* ======================================
              SHARED OBSERVATIONS
          ====================================== */}

          <section className="panel">

            <h3>
              Shared Observations (
              {comparison.sharedObservations.length})
            </h3>

            <p className="priority-description">
              Exact observations identified by both observers.
            </p>

            {comparison.sharedObservations.length > 0 ? (

              comparison.sharedObservations.map((item, index) => (
                <article
                  className="observation-group"
                  key={index}
                >

                  <h4 className="group-observation">
                    {item.observation}
                  </h4>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "repeat(auto-fit, minmax(220px, 1fr))",
                      gap: "12px",
                    }}
                  >

                    {/* OBSERVER A PERSPECTIVE */}

                    <div className="perspective-card">

                      <strong>
                        Observer A —{" "}
                        {formatText(item.findingA.agent)}
                      </strong>

                      <p>
                        <strong>Analysis Area:</strong>{" "}
                        {(item.findingA.analysis_area || [])
                          .map(formatText)
                          .join(", ") || "Not available"}
                      </p>

                      <FindingBadges finding={item.findingA} />

                    </div>

                    {/* OBSERVER B PERSPECTIVE */}

                    <div className="perspective-card">

                      <strong>
                        Observer B —{" "}
                        {formatText(item.findingB.agent)}
                      </strong>

                      <p>
                        <strong>Analysis Area:</strong>{" "}
                        {(item.findingB.analysis_area || [])
                          .map(formatText)
                          .join(", ") || "Not available"}
                      </p>

                      <FindingBadges finding={item.findingB} />

                    </div>

                  </div>

                </article>
              ))

            ) : (

              <p>
                No exact shared observations were identified
                between these two observers.
              </p>

            )}

          </section>

          {/* ======================================
              OBSERVER-SPECIFIC OBSERVATIONS
          ====================================== */}

          <section className="panel observer-specific-section">

            <h3>Observer-Specific Observations</h3>

            <p className="priority-description">
              Observations identified by one observer but not by
              the other.
            </p>

            <div
              className={`observer-specific-grid ${
                comparison.uniqueToA.length === 0 ||
                comparison.uniqueToB.length === 0
                  ? "single-unique-column"
                  : ""
              }`}
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(260px, 1fr))",
                gap: "16px",
              }}
            >

              {/* OBSERVER A */}

              <ComparisonColumn
                title={`Unique to Observer A — ${formatText(
                  comparison.reportA.primary_goal
                )}`}
                observerReport={comparison.reportA}
                uniqueFindings={comparison.uniqueToA}
              />

              {/* OBSERVER B */}

              <ComparisonColumn
                title={`Unique to Observer B — ${formatText(
                  comparison.reportB.primary_goal
                )}`}
                observerReport={comparison.reportB}
                uniqueFindings={comparison.uniqueToB}
              />

            </div>

          </section>

          {/* ======================================
              COMPARISON CONCLUSION
          ====================================== */}

          <section className="panel">

            <p className="eyebrow">
              COMPARISON SUMMARY
            </p>

            <h3>Observer Perspective Differences</h3>

            <p>
              Observer A (
              {formatText(comparison.reportA.primary_goal)})
              selected{" "}
              {comparison.reportA.selected_agent_count} specialist
              agent(s) and generated{" "}
              {comparison.reportA.total_findings} individual findings.
            </p>

            <p>
              Observer B (
              {formatText(comparison.reportB.primary_goal)})
              selected{" "}
              {comparison.reportB.selected_agent_count} specialist
              agent(s) and generated{" "}
              {comparison.reportB.total_findings} individual findings.
            </p>

            <p>
              Both observers identified{" "}
              {comparison.sharedObservations.length} exact shared
              observation(s).
            </p>

            <p>
              Observer A had {comparison.uniqueToA.length} unique
              observation(s), while Observer B had{" "}
              {comparison.uniqueToB.length} unique observation(s).
            </p>

            <p className="priority-note">
              Note: Shared observations are matched using normalized
              exact text, not semantic similarity. Priority values
              are preliminary category-based review defaults, not
              verified severity measurements.
            </p>

          </section>

        </section>
      )}

    </main>
  );
}

export default App;