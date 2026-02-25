import { Link } from "react-router-dom";

function Layout({ children }) {
  return (
    <div style={styles.wrapper}>
      <nav style={styles.navbar}>
        <div style={styles.logo}>Curricraft</div>

        <div style={styles.links}>
          <Link to="/" style={styles.link}>Create Session</Link>
          <Link to="/upload" style={styles.link}>Upload Data</Link>
          <Link to="/recommendations" style={styles.link}>Recommendations</Link>
          <Link to="/graduation-audit" style={styles.link}>Graduation Audit</Link>
          <Link to="/admin/courses" style={styles.link}>Admin</Link>
        </div>
      </nav>

      <main style={styles.content}>
        {children}
      </main>
    </div>
  );
}

const styles = {
  wrapper: {
    minHeight: "100vh",
    backgroundColor: "#f4f6f9",
  },
  navbar: {
    backgroundColor: "#111827",
    padding: "16px 40px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    color: "white",
  },
  logo: {
    fontSize: "18px",
    fontWeight: "bold",
  },
  links: {
    display: "flex",
    gap: "20px",
  },
  link: {
    color: "white",
    textDecoration: "none",
    fontSize: "14px",
  },
  content: {
    padding: "40px",
  },
};

export default Layout;