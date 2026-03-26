export default function Card({ title, children }) {
  return (
    <div style={{ border: '1px solid #eaeaea', borderRadius: '8px', padding: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '16px', backgroundColor: 'white' }}>
      {title && <h3 style={{ marginTop: 0, color: '#333' }}>{title}</h3>}
      {children}
    </div>
  );
}