import { useEffect, useState } from "react";

function Recommendations() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem("recommendation_result");
    if (stored) {
      setData(JSON.parse(stored));
    }
  }, []);

  if (!data) {
    return (
      <div style={styles.page}>
        <div style={styles.mainCard}>
          <h2 style={styles.pageTitle}>No Recommendation Data Found</h2>
          <p style={{ marginBottom: "20px" }}>
            Please upload transcript and generate recommendations first.
          </p>
          <button
            style={styles.button}
            onClick={() => (window.location.href = "/upload")}
          >
            Go To Upload Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <h1 style={styles.pageTitle}>Academic Recommendation Dashboard</h1>

      {/* ================= SUMMARY ================= */}
      <div style={styles.summaryGrid}>
        <div style={styles.summaryCard}>
          <h4 style={styles.cardLabel}>Earned Credits</h4>
          <p style={styles.bigNumber}>{data.earned_credits}</p>
        </div>

        <div style={styles.summaryCard}>
          <h4 style={styles.cardLabel}>Elective Status</h4>
          <p style={styles.cardText}>{data.elective_priority}</p>
        </div>

        <div style={styles.summaryCard}>
          <h4 style={styles.cardLabel}>Concentration</h4>
          <p style={styles.cardText}>
            {data.elective_progress?.track_status === "SELECTED"
              ? `Track ${data.elective_progress.chosen_group_id}`
              : "Not Selected"}
          </p>
        </div>
      </div>

      {/* ================= NEXT SEMESTER PLAN ================= */}
      <div style={styles.mainCard}>
        <h2 style={styles.sectionTitle}>
          Recommended Next Semester Plan
        </h2>

        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Course Code</th>
                <th style={styles.th}>Course Name</th>
                <th style={styles.th}>Credits</th>
                <th style={styles.th}>Source</th>
              </tr>
            </thead>
            <tbody>
              {data.next_semester_plan.recommended_courses.map(
                (course, i) => (
                  <tr
                    key={i}
                    style={{
                      backgroundColor:
                        i % 2 === 0 ? "#ffffff" : "#f9fafb",
                    }}
                  >
                    <td style={styles.td}>{course.course_code}</td>
                    <td style={styles.td}>{course.course_name}</td>
                    <td style={styles.td}>{course.credits}</td>
                    <td style={styles.td}>{course.source}</td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>

        <p style={styles.totalCredits}>
          Total Specialized Credits:{" "}
          {data.next_semester_plan.total_credits}
        </p>
      </div>

      {/* ================= ELECTIVE PROGRESS ================= */}
      {data.elective_progress && (
        <div style={styles.mainCard}>
          <h2 style={styles.sectionTitle}>Elective Progress</h2>

          <div style={styles.progressRow}>
            <span>From Chosen Track</span>
            <span>
              {data.elective_progress.chosen_group_completed} /{" "}
              {data.elective_progress.min_from_chosen_group}
            </span>
          </div>

          <div style={styles.progressRow}>
            <span>From All Groups</span>
            <span>
              {data.elective_progress.all_groups_completed} /{" "}
              {data.elective_progress.min_from_all_groups}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {
  page: {
    maxWidth: "1200px",
    margin: "0 auto",
  },

  pageTitle: {
    fontSize: "28px",
    fontWeight: "700",
    marginBottom: "35px",
  },

  summaryGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "20px",
    marginBottom: "40px",
  },

  summaryCard: {
    backgroundColor: "white",
    padding: "24px",
    borderRadius: "16px",
    boxShadow: "0 6px 18px rgba(0,0,0,0.06)",
    border: "1px solid #f1f5f9",
  },

  cardLabel: {
    fontSize: "14px",
    color: "#6b7280",
    marginBottom: "8px",
  },

  cardText: {
    fontSize: "16px",
    fontWeight: "500",
  },

  bigNumber: {
    fontSize: "36px",
    fontWeight: "700",
    color: "#2563eb",
  },

  mainCard: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "16px",
    boxShadow: "0 6px 18px rgba(0,0,0,0.06)",
    border: "1px solid #f1f5f9",
    marginBottom: "40px",
  },

  sectionTitle: {
    fontSize: "20px",
    fontWeight: "600",
    marginBottom: "20px",
  },

  tableWrapper: {
    overflowX: "auto",
  },

  table: {
    width: "100%",
    borderCollapse: "separate",
    borderSpacing: "0",
    fontSize: "14px",
  },

  th: {
    textAlign: "left",
    padding: "14px",
    backgroundColor: "#f3f4f6",
    fontWeight: "600",
    fontSize: "13px",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    borderBottom: "1px solid #e5e7eb",
  },

  td: {
    padding: "14px",
    borderBottom: "1px solid #f1f5f9",
  },

  totalCredits: {
    marginTop: "25px",
    fontWeight: "600",
    fontSize: "15px",
  },

  progressRow: {
    display: "flex",
    justifyContent: "space-between",
    padding: "14px 0",
    borderBottom: "1px solid #f1f5f9",
    fontSize: "14px",
  },

  button: {
    padding: "12px 20px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontWeight: "600",
    cursor: "pointer",
  },
};

export default Recommendations;