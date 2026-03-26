export default function Button({ children, onClick, type = "button", disabled = false }) {
  return (
    <button type={type} onClick={onClick} disabled={disabled} style={{ padding: '8px 16px', borderRadius: '4px', cursor: 'pointer',
     backgroundColor: '#0056b3', color: 'white', border: 'none', fontWeight: 'bold' }}>
      {children}
    </button>
  );
}