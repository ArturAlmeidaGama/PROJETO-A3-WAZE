import React, { useState } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState } from 'reactflow';
import axios from 'axios';
import 'reactflow/dist/style.css';

const nosIniciais = [
  { id: 'A', position: { x: 100, y: 250 }, data: { label: 'A (Início)' } },
  { id: 'C', position: { x: 300, y: 150 }, data: { label: 'C' } },
  { id: 'B', position: { x: 300, y: 350 }, data: { label: 'B' } },
  { id: 'D', position: { x: 500, y: 250 }, data: { label: 'D' } },
  { id: 'E', position: { x: 700, y: 250 }, data: { label: 'E (Fim)' } },
];

const arestasIniciais = [
  { id: 'A-B', source: 'A', target: 'B', label: '5 km', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'A-C', source: 'A', target: 'C', label: '2 km', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'C-B', source: 'C', target: 'B', label: '1 km', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'B-D', source: 'B', target: 'D', label: '2 km', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'C-D', source: 'C', target: 'D', label: '6 km', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'D-E', source: 'D', target: 'E', label: '3 km', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
];

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(nosIniciais);
  const [edges, setEdges, onEdgesChange] = useEdgesState(arestasIniciais);
  
  const [origem, setOrigem] = useState('');
  const [destino, setDestino] = useState('');
  
  // Novos estados para o bloqueio
  const [origemBloq, setOrigemBloq] = useState('');
  const [destinoBloq, setDestinoBloq] = useState('');
  
  const [mensagem, setMensagem] = useState('');

  // 1. LÓGICA DE CALCULAR ROTA
  const lidarComCalculo = async () => {
    try {
      setMensagem('Calculando...');
      const resposta = await axios.post('http://localhost:5000/calcular_rota', {
        inicio: origem, fim: destino
      });

      if (resposta.data.sucesso) {
        const rotaVencedora = resposta.data.rota;
        setMensagem(`Custo total: ${resposta.data.custo.toFixed(2)} km`);

        // Reseta o mapa, MAS mantém as ruas vermelhas de bloqueio intactas
        let novasArestas = edges.map(aresta => {
          if (aresta.style.stroke === '#ef4444') return aresta; // Ignora as bloqueadas (vermelhas)
          return { ...aresta, style: { strokeWidth: 2, stroke: '#b1b1b7' }, animated: false }; // Reseta as outras
        });

        // Pinta a nova rota de verde
        for (let i = 0; i < rotaVencedora.length - 1; i++) {
          const de = rotaVencedora[i];
          const para = rotaVencedora[i + 1];

          novasArestas = novasArestas.map(aresta => {
            if ((aresta.source === de && aresta.target === para) || 
                (aresta.source === para && aresta.target === de)) {
              return { ...aresta, style: { strokeWidth: 6, stroke: '#10b981' }, animated: true };
            }
            return aresta;
          });
        }
        setEdges(novasArestas);
      }
    } catch (erro) {
      setMensagem('❌ Rota impossível ou inválida!');
      // Reseta apenas a rota verde, mantendo bloqueios
      setEdges(eds => eds.map(e => e.style.stroke === '#ef4444' ? e : { ...e, style: { strokeWidth: 2, stroke: '#b1b1b7' }, animated: false }));
    }
  };

  // 2. LÓGICA DE BLOQUEAR RUA
  const lidarComBloqueio = async () => {
    try {
      setMensagem('Bloqueando...');
      const resposta = await axios.post('http://localhost:5000/bloquear_rua', {
        origem: origemBloq, destino: destinoBloq
      });

      if (resposta.data.sucesso) {
        setMensagem(`🚧 Rua ${origemBloq}-${destinoBloq} bloqueada!`);
        
        // Atualiza o visual da rua para vermelho tracejado
        setEdges(eds => eds.map(aresta => {
          if ((aresta.source === origemBloq && aresta.target === destinoBloq) || 
              (aresta.source === destinoBloq && aresta.target === origemBloq)) {
            return { 
              ...aresta, 
              style: { strokeWidth: 4, stroke: '#ef4444', strokeDasharray: '5,5' }, 
              animated: false 
            };
          }
          return aresta;
        }));
      }
    } catch (erro) {
      setMensagem('❌ Erro ao tentar bloquear.');
    }
  };

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', backgroundColor: '#f0f2f5' }}>
      
      {/* PAINEL DE CONTROLES */}
      <div style={{
        position: 'absolute', top: 20, left: 20, zIndex: 10,
        backgroundColor: 'white', padding: '20px', borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)', display: 'flex',
        flexDirection: 'column', gap: '15px', fontFamily: 'sans-serif', width: '250px'
      }}>
        
        {/* SEÇÃO 1: GPS */}
        <div>
          <h3 style={{ margin: '0 0 10px 0', borderBottom: '2px solid #f0f0f0', paddingBottom: '5px' }}>📍 GPS</h3>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input placeholder="De" maxLength={1} value={origem} onChange={(e) => setOrigem(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
            <input placeholder="Para" maxLength={1} value={destino} onChange={(e) => setDestino(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
          </div>
          <button onClick={lidarComCalculo} style={{ width: '100%', backgroundColor: '#10b981', color: 'white', padding: '10px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
            Calcular Nova Rota
          </button>
        </div>

        {/* SEÇÃO 2: INTERDIÇÕES */}
        <div>
          <h3 style={{ margin: '0 0 10px 0', borderBottom: '2px solid #f0f0f0', paddingBottom: '5px' }}>🚧 Acidente</h3>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input placeholder="Rua 1" maxLength={1} value={origemBloq} onChange={(e) => setOrigemBloq(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
            <input placeholder="Rua 2" maxLength={1} value={destinoBloq} onChange={(e) => setDestinoBloq(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
          </div>
          <button onClick={lidarComBloqueio} style={{ width: '100%', backgroundColor: '#ef4444', color: 'white', padding: '10px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
            Bloquear Rua
          </button>
        </div>

        {/* STATUS BAR */}
        <div style={{ backgroundColor: '#f8fafc', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
          <p style={{ margin: 0, fontWeight: 'bold', color: '#334155' }}>{mensagem || 'Aguardando comandos...'}</p>
        </div>

      </div>

      {/* MAPA */}
      <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} fitView>
        <Background color="#ccc" gap={16} />
        <Controls />
      </ReactFlow>

    </div>
  );
}

export default App;