import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { VRMLoaderPlugin } from "@pixiv/three-vrm";

function VrmViewer({ modelUrl, onVrmLoaded, onCanvasReady }) {
  const containerRef = useRef(null);

  useEffect(() => {
    // React 18 StrictModeの開発時二重実行で、破棄済みのeffectのVRM読み込みが
    // 後から解決してonVrmLoadedを呼んでしまうのを防ぐガード
    let cancelled = false;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xdddddd);

    const camera = new THREE.PerspectiveCamera(30, width / height, 0.1, 20);
    camera.position.set(0, 1.3, 3);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);
    if (!cancelled && onCanvasReady) onCanvasReady(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 1.0, 0);
    controls.update();

    const light = new THREE.DirectionalLight(0xffffff, Math.PI);
    light.position.set(1, 1, 1);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    let currentVrm = null;
    loader.load(modelUrl, (gltf) => {
      if (cancelled) return;
      const vrm = gltf.userData.vrm;
      scene.add(vrm.scene);
      currentVrm = vrm;
      if (onVrmLoaded) onVrmLoaded(vrm);
    });

    const clock = new THREE.Clock();
    let frameId;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      if (currentVrm) currentVrm.update(delta);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelled = true;
      cancelAnimationFrame(frameId);
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, [modelUrl, onVrmLoaded, onCanvasReady]);

  return <div ref={containerRef} style={{ width: "600px", height: "600px" }} />;
}

export default VrmViewer;
