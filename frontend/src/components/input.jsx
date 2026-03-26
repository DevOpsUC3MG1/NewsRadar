export default function Input({ label, type = "text", value, onChange, placeholder }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', marginBottom: '10px' }}>
      {label && <label style={{ marginBottom: '4px', fontWeight: 'bold', color: '#333' }}>{label}</label>}
      <input type={type} value={value} onChange={onChange} placeholder={placeholder} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }} />
    </div>
  );
}