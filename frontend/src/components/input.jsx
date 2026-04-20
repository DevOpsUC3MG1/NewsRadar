import { forwardRef } from 'react';

const Input = forwardRef(({ label, type = "text", className, labelClassName, error, ...props }, ref) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', marginBottom: '20px' }}>
      {label && (
        <label 
          className={labelClassName} 
          style={labelClassName ? undefined : { marginBottom: '4px', fontWeight: 'bold', color: '#333' }}
        >
          {label}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        className={className}
        style={className ? undefined : { padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
        {...props}
      />
      {/* Si hay error, lo mostramos automáticamente */}
      {error && (
        <span style={{ color: '#e74c3c', fontSize: '0.8rem', marginTop: '5px' }}>
          {error}
        </span>
      )}
    </div>
  );
});

Input.displayName = "Input";
export default Input;