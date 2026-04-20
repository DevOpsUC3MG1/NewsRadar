export default function Button({ children, className, type = "button", disabled = false, ...props }) {
  return (
    <button
      type={type}
      disabled={disabled}
      className={className}
      {...props}
      style={className ? undefined : { padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', backgroundColor: '#0056b3', color: 'white', border: 'none', fontWeight: 'bold' }}
    >
      {children}
    </button>
  );
}