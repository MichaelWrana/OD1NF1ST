/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  removeElements,
  Background,
  isNode,
  Controls,
} from 'react-flow-renderer';
import dagre from 'dagre';
import initialElements from './initial-elements';
import './layouting.css';
import { ax } from '../../api';

import DeviceNode from './DeviceNode';
import GadgetNode from './GadgetNode';
const nodeTypes = {
  device: DeviceNode,
  gadget: GadgetNode
};
const snapGrid = [20, 20];

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));
const getLayoutedElements = (elements, direction = 'LR') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });
  elements.forEach((el) => {
    if (isNode(el)) {
      dagreGraph.setNode(el.id, { width: 150, height: 50 });
    } else {
      dagreGraph.setEdge(el.source, el.target);
    }
  });
  dagre.layout(dagreGraph);
  return elements.map((el) => {
    if (isNode(el)) {
      const nodeWithPosition = dagreGraph.node(el.id);
      el.targetPosition = isHorizontal ? 'left' : 'top';
      el.sourcePosition = isHorizontal ? 'right' : 'bottom';
      // unfortunately we need this little hack to pass a slighltiy different position
      // in order to notify react flow about the change
      el.position = {
        x: nodeWithPosition.x + Math.random() / 1000,
        y: nodeWithPosition.y,
      };
    }
    return el;
  });
};
const layoutedElements = [];
const SystemFlow = props => {
  const [elements, setElements] = useState(layoutedElements);
  const [current, setCurrent] = useState(props.current)

  useEffect(async () => {
    // setCurrent(props.current)
    // setTimeout(() => {
    const intervalId = setInterval(() => {
      ax.get('api/get_sim').then(result => {
        if (result.data.flow)
          setElements(getLayoutedElements(result.data.flow));
      })
      return () => clearInterval(intervalId);
    }, 1000);
    // }, 500)

  }, []);// Pass in empty array to run only once!

  const onConnect = (params) =>
    setElements((els) =>
      addEdge({ ...params, type: 'smoothstep', animated: true }, els)
    );
  const onElementsRemove = (elementsToRemove) =>
    setElements((els) => removeElements(elementsToRemove, els));
  const onLayout = useCallback(
    (direction) => {
      const layoutedElements = getLayoutedElements(elements, direction);
      setElements(layoutedElements);
    },
    [elements]
  );
  return (
    <div className="layoutflow g-panel-right">
      <ReactFlowProvider>
        <ReactFlow
          elements={elements}
          onConnect={onConnect}
          onElementsRemove={onElementsRemove}
          connectionLineType="smoothstep"
          elementsSelectable={true}
          nodesConnectable={false}
          snapToGrid={true}
          snapGrid={snapGrid}
          nodeTypes={nodeTypes}
        >
          <Controls />
          <Background color="#aaa" gap={16} />
        </ReactFlow>
        <div className="controls">
          {/* <button onClick={() => onLayout('TB')}>vertical layout</button> */}
          {/* <button className="btn btn-sm btn-info" onClick={() => onLayout('LR')}>Rest Layout</button> */}
        </div>
      </ReactFlowProvider>
    </div>
  );
};
export default SystemFlow;