export default function Table({ headers, data }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '16px', color: '#333' }}>
      <thead>
        <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
          {headers.map((header, index) => (
            <th key={index} style={{ padding: '12px', textAlign: 'left' }}>{header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, rowIndex) => (
          <tr key={rowIndex} style={{ borderBottom: '1px solid #ddd' }}>
            {Object.values(row).map((cell, cellIndex) => (
              <td key={cellIndex} style={{ padding: '12px' }}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}