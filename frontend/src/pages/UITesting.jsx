import { useState } from 'react';
// Actualizamos las rutas para que salgan de 'pages' y entren en 'components'
import Button from '../components/button';
import Input from '../components/input';
import Card from '../components/card';
import Badge from '../components/badge';
import Table from '../components/table';
import Modal from '../components/modal';

export default function UiTesting() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");

  const tableHeaders = ["Fuente", "Categoría", "Estado"];
  const tableData = [
    { fuente: "El País", categoria: "Política", estado: <Badge text="Activo" color="#28a745" /> },
    { fuente: "X/Twitter", categoria: "Tecnología", estado: <Badge text="Inactivo" color="#dc3545" /> },
  ];

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h1>UI Testing - NewsRadar</h1>

      <Card title="Prueba de Input y Botón">
        <Input
          label="Buscar nueva fuente RSS"
          placeholder="Ej: https://rss.nytimes.com..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <Button onClick={() => alert(`Buscando: ${inputValue}`)}>Buscar Fuente</Button>
      </Card>

      <Card title="Prueba de Tabla y Badges">
        <Table headers={tableHeaders} data={tableData} />
      </Card>

      <Card title="Prueba de Modal">
        <Button onClick={() => setIsModalOpen(true)}>Abrir Modal de Confirmación</Button>
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Confirmar Acción">
        <p>¿Estás seguro de que deseas eliminar esta alerta?</p>
        <Button onClick={() => setIsModalOpen(false)}>Sí, eliminar</Button>
      </Modal>
    </div>
  );
}