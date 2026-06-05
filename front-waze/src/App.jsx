import React, { useState } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState } from 'reactflow';
import axios from 'axios';
import 'reactflow/dist/style.css';

const nosPadrao = [
  { id: 'A', position: { x: 100, y: 250 }, data: { label: 'A' } },
  { id: 'C', position: { x: 300, y: 150 }, data: { label: 'C' } },
  { id: 'B', position: { x: 300, y: 350 }, data: { label: 'B' } },
  { id: 'D', position: { x: 500, y: 250 }, data: { label: 'D' } },
  { id: 'E', position: { x: 700, y: 250 }, data: { label: 'E' } },
];
const arestasPadrao = [
  { id: 'A-B', source: 'A', target: 'B', label: '5 km | 10 min', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'A-C', source: 'A', target: 'C', label: '2 km | 3 min', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'C-B', source: 'C', target: 'B', label: '1 km | 2 min', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'B-D', source: 'B', target: 'D', label: '2 km | 2 min', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'C-D', source: 'C', target: 'D', label: '6 km | 8 min', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
  { id: 'D-E', source: 'D', target: 'E', label: '3 km | 4 min', style: { strokeWidth: 2, stroke: '#b1b1b7' } },
];

function App() {
  const [fase, setFase] = useState(0);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [mensagem, setMensagem] = useState('');

  // Construtor
  const [novaOrigem, setNovaOrigem] = useState('');
  const [novoDestino, setNovoDestino] = useState('');
  const [novaDistancia, setNovaDistancia] = useState('');
  const [novoTempo, setNovoTempo] = useState('');

  // GPS
  const [origem, setOrigem] = useState('');
  const [destino, setDestino] = useState('');
  const [criterio, setCriterio] = useState('distancia');
  const [origemBloq, setOrigemBloq] = useState('');
  const [destinoBloq, setDestinoBloq] = useState('');

  const iniciarMapaPadrao = async () => {
    try {
      await axios.post('http://localhost:5000/mapa_padrao');
      setNodes(nosPadrao); setEdges(arestasPadrao); setFase(2);
      setMensagem('Mapa padrão carregado!');
    } catch (e) { alert('Erro ao conectar com o Backend.'); }
  };

  const iniciarMapaDoZero = async () => {
    try {
      await axios.post('http://localhost:5000/resetar_mapa');
      setNodes([]); setEdges([]); setFase(1);
      setMensagem('Modo Construtor Ativado.');
    } catch (e) { alert('Erro ao conectar com o Backend.'); }
  };

  const adicionarRua = async () => {
    if (!novaOrigem || !novoDestino || !novaDistancia || !novoTempo) {
      setMensagem('❌ Preencha todos os campos!');
      return;
    }

    // --- CORREÇÃO DO ERRO 2: Bloqueia 0 ou Negativos no Front ---
    if (parseFloat(novaDistancia) <= 0 || parseFloat(novoTempo) <= 0) {
      setMensagem('❌ Distância e Tempo devem ser maiores que zero!');
      return;
    }

    if (novaOrigem === novoDestino) {
      setMensagem('❌ A origem não pode ser igual ao destino!');
      return;
    }

    try {
      setMensagem('Adicionando...');
      const resposta = await axios.post('http://localhost:5000/adicionar_rua', {
        origem: novaOrigem, destino: novoDestino,
        distancia: parseFloat(novaDistancia), tempo: parseFloat(novoTempo)
      });

      if (resposta.data.sucesso) {
        const novosNodes = [...nodes];
        const posAleatoria = () => ({ x: Math.random() * 400 + 100, y: Math.random() * 400 + 100 });

        if (!novosNodes.find(n => n.id === novaOrigem)) {
          novosNodes.push({ id: novaOrigem, position: posAleatoria(), data: { label: novaOrigem } });
        }
        if (!novosNodes.find(n => n.id === novoDestino)) {
          novosNodes.push({ id: novoDestino, position: posAleatoria(), data: { label: novoDestino } });
        }

        const novaAresta = {
          id: `${novaOrigem}-${novoDestino}`, source: novaOrigem, target: novoDestino,
          label: `${novaDistancia}km | ${novoTempo}min`,
          style: { strokeWidth: 2, stroke: '#b1b1b7' }
        };

        setNodes(novosNodes);
        setEdges([...edges, novaAresta]);
        setMensagem(`✅ Rua ${novaOrigem}-${novoDestino} adicionada!`);
        setNovaOrigem(''); setNovoDestino(''); setNovaDistancia(''); setNovoTempo('');
      }
    } catch (erro) {
      setMensagem(erro.response?.data?.mensagem || '❌ Erro ao adicionar rua.');
    }
  };

  const lidarComCalculo = async () => {
    if (origem === destino) {
      setMensagem('⚠️ Você já está no destino!');
      return;
    }
    try {
      setMensagem('Calculando...');
      const resposta = await axios.post('http://localhost:5000/calcular_rota', {
        inicio: origem, fim: destino, criterio: criterio
      });

      if (resposta.data.sucesso) {
        const rotaVencedora = resposta.data.rota;
        const unidade = criterio === 'distancia' ? 'km' : 'min';
        setMensagem(`🏆 Custo total: ${resposta.data.custo.toFixed(2)} ${unidade}`);

        let novasArestas = edges.map(aresta => {
          if (aresta.style.stroke === '#ef4444') return aresta; 
          return { ...aresta, style: { strokeWidth: 2, stroke: '#b1b1b7' }, animated: false };
        });

        for (let i = 0; i < rotaVencedora.length - 1; i++) {
          const de = rotaVencedora[i]; const para = rotaVencedora[i + 1];
          novasArestas = novasArestas.map(aresta => {
            if ((aresta.source === de && aresta.target === para) || (aresta.source === para && aresta.target === de)) {
              return { ...aresta, style: { strokeWidth: 6, stroke: '#10b981' }, animated: true };
            }
            return aresta;
          });
        }
        setEdges(novasArestas);
      }
    } catch (erro) {
      setMensagem('🚧 Rota impossível ou inexistente!');
      setEdges(eds => eds.map(e => e.style.stroke === '#ef4444' ? e : { ...e, style: { strokeWidth: 2, stroke: '#b1b1b7' }, animated: false }));
    }
  };

  const lidarComBloqueio = async () => {
    try {
      setMensagem('Bloqueando...');
      const resposta = await axios.post('http://localhost:5000/bloquear_rua', {
        origem: origemBloq, destino: destinoBloq
      });

      if (resposta.data.sucesso) {
        setMensagem(`🚧 Rua ${origemBloq}-${destinoBloq} bloqueada!`);
        setEdges(eds => eds.map(aresta => {
          if ((aresta.source === origemBloq && aresta.target === destinoBloq) || (aresta.source === destinoBloq && aresta.target === origemBloq)) {
            return { ...aresta, style: { strokeWidth: 4, stroke: '#ef4444', strokeDasharray: '5,5' }, animated: false };
          }
          return aresta;
        }));
      }
    } catch (erro) { setMensagem('❌ Rua não existe ou já bloqueada.'); }
  };

  // --- CORREÇÃO DO ERRO 1: Função para Liberar a Rua ---
  const lidarComLiberacao = async () => {
    try {
      setMensagem('Liberando...');
      const resposta = await axios.post('http://localhost:5000/liberar_rua', {
        origem: origemBloq, destino: destinoBloq
      });

      if (resposta.data.sucesso) {
        setMensagem(`✅ Rua ${origemBloq}-${destinoBloq} liberada!`);
        setEdges(eds => eds.map(aresta => {
          if ((aresta.source === origemBloq && aresta.target === destinoBloq) || (aresta.source === destinoBloq && aresta.target === origemBloq)) {
            // Volta para o estilo cinza original
            return { ...aresta, style: { strokeWidth: 2, stroke: '#b1b1b7' }, animated: false };
          }
          return aresta;
        }));
      }
    } catch (erro) { setMensagem('❌ Erro ao tentar liberar.'); }
  };

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', backgroundColor: '#f0f2f5' }}>
      
      {fase === 0 && (
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 50, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
          <h1>🧭 Simulador de Rotas Web</h1>
          <p>Como você quer começar?</p>
          <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
            <button onClick={iniciarMapaPadrao} style={{ padding: '15px 30px', fontSize: '16px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>Usar Mapa Padrão</button>
            <button onClick={iniciarMapaDoZero} style={{ padding: '15px 30px', fontSize: '16px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>Criar Mapa do Zero</button>
          </div>
        </div>
      )}

      {fase > 0 && (
        <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 10, backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', display: 'flex', flexDirection: 'column', gap: '15px', fontFamily: 'sans-serif', width: '280px' }}>
          
          {fase === 1 && (
            <div>
              <h3 style={{ margin: '0 0 10px 0', borderBottom: '2px solid #f0f0f0', paddingBottom: '5px' }}>🏗️ Adicionar Rua</h3>
              <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <input placeholder="Origem" maxLength={1} value={novaOrigem} onChange={(e) => setNovaOrigem(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
                <input placeholder="Destino" maxLength={1} value={novoDestino} onChange={(e) => setNovoDestino(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
              </div>
              <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                {/* min="0.1" impede cliques nativos em números negativos */}
                <input type="number" min="0.1" step="0.1" placeholder="Dist (km)" value={novaDistancia} onChange={(e) => setNovaDistancia(e.target.value)} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
                <input type="number" min="0.1" step="0.1" placeholder="Tempo (min)" value={novoTempo} onChange={(e) => setNovoTempo(e.target.value)} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
              </div>
              <button onClick={adicionarRua} style={{ width: '100%', backgroundColor: '#3b82f6', color: 'white', padding: '10px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', marginBottom: '10px' }}>+ Adicionar Conexão</button>
              <button onClick={() => setFase(2)} style={{ width: '100%', backgroundColor: '#64748b', color: 'white', padding: '10px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>✅ Finalizar Mapa</button>
            </div>
          )}

          {fase === 2 && (
            <>
              <div>
                <h3 style={{ margin: '0 0 10px 0', borderBottom: '2px solid #f0f0f0', paddingBottom: '5px' }}>📍 GPS</h3>
                <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                  <input placeholder="De" maxLength={1} value={origem} onChange={(e) => setOrigem(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
                  <input placeholder="Para" maxLength={1} value={destino} onChange={(e) => setDestino(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
                </div>
                <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'center', gap: '10px' }}>
                  <label><input type="radio" name="criterio" value="distancia" checked={criterio === 'distancia'} onChange={(e) => setCriterio(e.target.value)} /> Distância</label>
                  <label><input type="radio" name="criterio" value="tempo" checked={criterio === 'tempo'} onChange={(e) => setCriterio(e.target.value)} /> Tempo</label>
                </div>
                <button onClick={lidarComCalculo} style={{ width: '100%', backgroundColor: '#10b981', color: 'white', padding: '10px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Calcular Nova Rota</button>
              </div>

              <div>
                <h3 style={{ margin: '0 0 10px 0', borderBottom: '2px solid #f0f0f0', paddingBottom: '5px' }}>🚧 Trânsito / Acidente</h3>
                <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                  <input placeholder="Rua 1" maxLength={1} value={origemBloq} onChange={(e) => setOrigemBloq(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
                  <input placeholder="Rua 2" maxLength={1} value={destinoBloq} onChange={(e) => setDestinoBloq(e.target.value.toUpperCase())} style={{ width: '100%', textAlign: 'center', padding: '5px' }} />
                </div>
                
                {/* BOTÕES LADO A LADO: Bloquear e Liberar */}
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button onClick={lidarComBloqueio} style={{ width: '50%', backgroundColor: '#ef4444', color: 'white', padding: '10px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Bloquear</button>
                  <button onClick={lidarComLiberacao} style={{ width: '50%', backgroundColor: '#3b82f6', color: 'white', padding: '10px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Liberar</button>
                </div>
              </div>
            </>
          )}

          <div style={{ backgroundColor: '#f8fafc', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
            <p style={{ margin: 0, fontWeight: 'bold', color: '#334155' }}>{mensagem || 'Aguardando comandos...'}</p>
          </div>

        </div>
      )}

      <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} fitView>
        <Background color="#ccc" gap={16} />
        <Controls />
      </ReactFlow>

    </div>
  );
}

export default App;