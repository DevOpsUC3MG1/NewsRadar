export default function Badge({ text, color = "#28a745" }) {
  return (
    <span style={{ backgroundColor: color, color: 'white', padding: '4px 8px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 'bold' }}>
      {text}
    </span>
  );
}