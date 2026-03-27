import { useState } from 'react'
import reactLogo from '../assets/react.svg'
import viteLogo from '../assets/vite.svg'
import heroImg from '../assets/hero.png'
import '../assets/App.css'

// 👇 1. Importamos tu nuevo componente de gráfico
import ExampleNewCharts from '../components/ExampleNewCharts'

function Home() {
  const [count, setCount] = useState(0)

  return (
    <>
      <section id="center">
        <div>
          <h1>Get started</h1>
          <p>
            Edit <code>src/pages/Home.jsx</code> and save to test <code>HMR</code>
          </p>
        </div>
        <button
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>

      <div className="ticks"></div>

      {/* 👇 2. Aquí añadimos la nueva sección exclusiva para tu gráfico */}
      <section id="chart-section" style={{ padding: '2rem 0', textAlign: 'center' }}>
        <h2>Ejemplo de Gráfico Recharts</h2>
        <p style={{ marginBottom: '2rem' }}>Así se ven las estadísticas de NewsRadar:</p>

        {/* Aquí renderizamos el componente */}
        <ExampleNewCharts />
      </section>

      <div className="ticks"></div>



    </>
  )
}

// Cambiado de "export default App" a "export default Home" para mantener el orden
export default Home