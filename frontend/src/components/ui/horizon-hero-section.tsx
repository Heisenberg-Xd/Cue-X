import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

gsap.registerPlugin(ScrollTrigger);

export const HorizonHeroSection = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef    = useRef<HTMLCanvasElement>(null);
  const titleRef     = useRef<HTMLHeadingElement>(null);
  const subtitleRef  = useRef<HTMLDivElement>(null);
  const scrollProgressRef = useRef<HTMLDivElement>(null);
  const menuRef      = useRef<HTMLDivElement>(null);

  const smoothCameraPos = useRef({ x: 0, y: 30, z: 100 });

  const [scrollProgress, setScrollProgress] = useState(0);
  const [currentSection, setCurrentSection] = useState(0);
  const [isReady, setIsReady] = useState(false);
  const totalSections = 2;

  const threeRefs = useRef<{
    scene: THREE.Scene | null;
    camera: THREE.PerspectiveCamera | null;
    renderer: THREE.WebGLRenderer | null;
    composer: EffectComposer | null;
    stars: THREE.Points[];
    nebula: THREE.Mesh | null;
    mountains: THREE.Mesh[];
    animationId: number | null;
    targetCameraX?: number;
    targetCameraY?: number;
    targetCameraZ?: number;
    locations: number[];
  }>({
    scene: null, camera: null, renderer: null, composer: null,
    stars: [], nebula: null, mountains: [], animationId: null, locations: []
  });

  /* ── Three.js Init ──────────────────────────────────────────── */
  useEffect(() => {
    const { current: refs } = threeRefs;

    // Scene
    refs.scene = new THREE.Scene();
    refs.scene.fog = new THREE.FogExp2(0x000000, 0.00025);

    // Camera
    refs.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
    refs.camera.position.z = 100;
    refs.camera.position.y = 20;

    // Renderer
    if (!canvasRef.current) return;
    refs.renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current, antialias: true, alpha: true });
    refs.renderer.setSize(window.innerWidth, window.innerHeight);
    refs.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    refs.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    refs.renderer.toneMappingExposure = 0.5;

    // Post-processing
    refs.composer = new EffectComposer(refs.renderer);
    refs.composer.addPass(new RenderPass(refs.scene, refs.camera));
    refs.composer.addPass(new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight), 0.8, 0.4, 0.85
    ));

    // Stars
    const starCount = 5000;
    for (let i = 0; i < 3; i++) {
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(starCount * 3);
      const colors    = new Float32Array(starCount * 3);
      const sizes     = new Float32Array(starCount);
      for (let j = 0; j < starCount; j++) {
        const radius = 200 + Math.random() * 800;
        const theta  = Math.random() * Math.PI * 2;
        const phi    = Math.acos(Math.random() * 2 - 1);
        positions[j*3]   = radius * Math.sin(phi) * Math.cos(theta);
        positions[j*3+1] = radius * Math.sin(phi) * Math.sin(theta);
        positions[j*3+2] = radius * Math.cos(phi);
        const color = new THREE.Color();
        const c = Math.random();
        if (c < 0.7) color.setHSL(0, 0, 0.8 + Math.random() * 0.2);
        else if (c < 0.9) color.setHSL(0.08, 0.5, 0.8);
        else color.setHSL(0.6, 0.5, 0.8);
        colors[j*3] = color.r; colors[j*3+1] = color.g; colors[j*3+2] = color.b;
        sizes[j] = Math.random() * 2 + 0.5;
      }
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color',    new THREE.BufferAttribute(colors, 3));
      geometry.setAttribute('size',     new THREE.BufferAttribute(sizes, 1));
      const mat = new THREE.ShaderMaterial({
        uniforms: { time: { value: 0 }, depth: { value: i } },
        vertexShader: `
          attribute float size; attribute vec3 color; varying vec3 vColor;
          uniform float time; uniform float depth;
          void main() {
            vColor = color; vec3 pos = position;
            float angle = time * 0.05 * (1.0 - depth * 0.3);
            mat2 rot = mat2(cos(angle),-sin(angle),sin(angle),cos(angle));
            pos.xy = rot * pos.xy;
            vec4 mv = modelViewMatrix * vec4(pos,1.0);
            gl_PointSize = size * (300.0 / -mv.z);
            gl_Position = projectionMatrix * mv;
          }`,
        fragmentShader: `
          varying vec3 vColor;
          void main() {
            float d = length(gl_PointCoord - vec2(0.5));
            if (d > 0.5) discard;
            gl_FragColor = vec4(vColor, 1.0 - smoothstep(0.0,0.5,d));
          }`,
        transparent: true, blending: THREE.AdditiveBlending, depthWrite: false
      });
      const stars = new THREE.Points(geometry, mat);
      refs.scene.add(stars);
      refs.stars.push(stars);
    }

    // Nebula
    const nebGeom = new THREE.PlaneGeometry(8000, 4000, 100, 100);
    const nebMat = new THREE.ShaderMaterial({
      uniforms: {
        time:    { value: 0 },
        color1:  { value: new THREE.Color(0x0033ff) },
        color2:  { value: new THREE.Color(0xff0066) },
        opacity: { value: 0.3 }
      },
      vertexShader: `
        varying vec2 vUv; varying float vEl; uniform float time;
        void main() {
          vUv = uv; vec3 p = position;
          float el = sin(p.x*0.01+time)*cos(p.y*0.01+time)*20.0;
          p.z += el; vEl = el;
          gl_Position = projectionMatrix*modelViewMatrix*vec4(p,1.0);
        }`,
      fragmentShader: `
        uniform vec3 color1,color2; uniform float opacity,time;
        varying vec2 vUv; varying float vEl;
        void main() {
          float m = sin(vUv.x*10.0+time)*cos(vUv.y*10.0+time);
          vec3 c = mix(color1,color2,m*0.5+0.5);
          float a = max(0.0, opacity*(1.0-length(vUv-0.5)*2.0) + vEl*0.01);
          gl_FragColor = vec4(c,a);
        }`,
      transparent: true, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, depthWrite: false
    });
    const nebula = new THREE.Mesh(nebGeom, nebMat);
    nebula.position.z = -1050;
    refs.scene.add(nebula);
    refs.nebula = nebula;

    // Mountains
    const layers = [
      { distance: -50,  height: 60,  color: 0x1a1a2e, opacity: 1   },
      { distance: -100, height: 80,  color: 0x16213e, opacity: 0.8 },
      { distance: -150, height: 100, color: 0x0f3460, opacity: 0.6 },
      { distance: -200, height: 120, color: 0x0a4668, opacity: 0.4 },
    ];
    const locations: number[] = [];
    layers.forEach((layer, index) => {
      const pts: THREE.Vector2[] = [];
      for (let i = 0; i <= 50; i++) {
        const x = (i/50 - 0.5)*1000;
        const y = Math.sin(i*0.1)*layer.height + Math.sin(i*0.05)*layer.height*0.5 + Math.random()*layer.height*0.2 - 100;
        pts.push(new THREE.Vector2(x, y));
      }
      pts.push(new THREE.Vector2(5000,-300), new THREE.Vector2(-5000,-300));
      const msh = new THREE.Mesh(
        new THREE.ShapeGeometry(new THREE.Shape(pts)),
        new THREE.MeshBasicMaterial({ color: layer.color, transparent: true, opacity: layer.opacity, side: THREE.DoubleSide })
      );
      msh.position.z = layer.distance;
      msh.position.y = layer.distance;
      msh.userData = { baseZ: layer.distance, index };
      refs.scene!.add(msh);
      refs.mountains.push(msh);
      locations[index] = layer.distance;
    });
    refs.locations = locations;

    // Atmosphere
    refs.scene.add(new THREE.Mesh(
      new THREE.SphereGeometry(600, 32, 32),
      new THREE.ShaderMaterial({
        uniforms: { time: { value: 0 } },
        vertexShader: `varying vec3 vN; void main(){ vN=normalize(normalMatrix*normal); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
        fragmentShader: `varying vec3 vN; uniform float time;
          void main(){
            float i=pow(0.7-dot(vN,vec3(0,0,1)),2.0);
            vec3 a=vec3(0.3,0.6,1.0)*i*(sin(time*2.0)*0.1+0.9);
            gl_FragColor=vec4(a,i*0.25);
          }`,
        side: THREE.BackSide, blending: THREE.AdditiveBlending, transparent: true
      })
    ));

    refs.targetCameraX = 0; refs.targetCameraY = 30; refs.targetCameraZ = 300;

    // Animate loop
    const animate = () => {
      refs.animationId = requestAnimationFrame(animate);
      const t = Date.now() * 0.001;
      refs.stars.forEach(s => { if (s.material instanceof THREE.ShaderMaterial) s.material.uniforms.time.value = t; });
      if (refs.nebula?.material instanceof THREE.ShaderMaterial) refs.nebula.material.uniforms.time.value = t*0.5;
      if (refs.camera && refs.targetCameraX !== undefined && refs.targetCameraY !== undefined && refs.targetCameraZ !== undefined) {
        const k = 0.05;
        smoothCameraPos.current.x += (refs.targetCameraX - smoothCameraPos.current.x)*k;
        smoothCameraPos.current.y += (refs.targetCameraY - smoothCameraPos.current.y)*k;
        smoothCameraPos.current.z += (refs.targetCameraZ - smoothCameraPos.current.z)*k;
        refs.camera.position.x = smoothCameraPos.current.x + Math.sin(t*0.1)*2;
        refs.camera.position.y = smoothCameraPos.current.y + Math.cos(t*0.15)*1;
        refs.camera.position.z = smoothCameraPos.current.z;
        refs.camera.lookAt(0, 10, -600);
      }
      refs.mountains.forEach((m, i) => {
        m.position.x = Math.sin(t*0.1)*2*(1+i*0.5);
        m.position.y = 50 + Math.cos(t*0.15)*(1+i*0.5);
      });
      refs.composer?.render();
    };
    animate();

    const handleResize = () => {
      if (refs.camera && refs.renderer && refs.composer) {
        refs.camera.aspect = window.innerWidth / window.innerHeight;
        refs.camera.updateProjectionMatrix();
        refs.renderer.setSize(window.innerWidth, window.innerHeight);
        refs.composer.setSize(window.innerWidth, window.innerHeight);
      }
    };
    window.addEventListener('resize', handleResize);
    setIsReady(true);

    return () => {
      if (refs.animationId) cancelAnimationFrame(refs.animationId);
      window.removeEventListener('resize', handleResize);
      refs.stars.forEach(s => { s.geometry.dispose(); if (s.material instanceof THREE.Material) s.material.dispose(); });
      refs.mountains.forEach(m => { m.geometry.dispose(); if (m.material instanceof THREE.Material) m.material.dispose(); });
      if (refs.nebula) { refs.nebula.geometry.dispose(); if (refs.nebula.material instanceof THREE.Material) refs.nebula.material.dispose(); }
      refs.renderer?.dispose();
    };
  }, []);

  /* ── GSAP entrance ──────────────────────────────────────────── */
  useEffect(() => {
    if (!isReady) return;
    gsap.set([menuRef.current, titleRef.current, subtitleRef.current, scrollProgressRef.current], { visibility: 'visible' });
    const tl = gsap.timeline();
    if (menuRef.current)   tl.from(menuRef.current, { x: -100, opacity: 0, duration: 1, ease: 'power3.out' });
    if (titleRef.current)  tl.from(titleRef.current, { y: 200, opacity: 0, duration: 1.5, ease: 'power4.out' }, '-=0.5');
    if (subtitleRef.current) {
      tl.from(Array.from(subtitleRef.current.children), { y: 50, opacity: 0, duration: 1, stagger: 0.2, ease: 'power3.out' }, '-=0.8');
    }
    if (scrollProgressRef.current) tl.from(scrollProgressRef.current, { opacity: 0, y: 50, duration: 1, ease: 'power2.out' }, '-=0.5');
    return () => { tl.kill(); };
  }, [isReady]);

  /* ── Scroll handling ────────────────────────────────────────── */
  useEffect(() => {
    const handleScroll = () => {
      const scrollY  = window.scrollY;
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      const progress  = maxScroll > 0 ? Math.min(scrollY / maxScroll, 1) : 0;
      setScrollProgress(progress);
      setCurrentSection(Math.min(Math.floor(progress * totalSections), totalSections - 1));

      const { current: refs } = threeRefs;
      const totalProgress   = progress * totalSections;
      const sectionProgress = totalProgress % 1;
      const camPos = [
        { x: 0, y: 30, z: 300 },
        { x: 0, y: 40, z: -50 },
        { x: 0, y: 50, z: -700 },
      ];
      const cur  = camPos[Math.floor(totalProgress)] || camPos[0];
      const next = camPos[Math.min(Math.floor(totalProgress)+1, camPos.length-1)];
      refs.targetCameraX = cur.x + (next.x - cur.x) * sectionProgress;
      refs.targetCameraY = cur.y + (next.y - cur.y) * sectionProgress;
      refs.targetCameraZ = cur.z + (next.z - cur.z) * sectionProgress;

      refs.mountains.forEach((mountain, i) => {
        mountain.position.z = progress > 0.7 ? 600000 : (refs.locations[i] ?? mountain.userData.baseZ);
      });
      if (refs.nebula && refs.mountains[3]) refs.nebula.position.z = refs.mountains[3].position.z;
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, [totalSections]);

  /* ── Section data ───────────────────────────────────────────── */
  const sections = [
    { title: 'HORIZON',  line1: 'Where vision meets reality,',               line2: 'we shape the future of tomorrow'        },
    { title: 'COSMOS',   line1: 'Beyond the boundaries of imagination,',     line2: 'lies the universe of possibilities'     },
    { title: 'INFINITY', line1: 'In the space between thought and creation,', line2: 'we find the essence of true innovation' },
  ];

  // Opacity for the fixed first-section hero — fades out as user scrolls
  const heroOpacity = Math.max(0, 1 - scrollProgress * totalSections * 2.5);

  return (
    <>
      {/* ── Scoped styles ── */}
      <style>{`
        .hero-container {
          position: relative;
          width: 100%;
          background: #000;
          color: #fff;
        }
        .hero-canvas {
          position: fixed;
          top: 0; left: 0;
          width: 100%; height: 100%;
          pointer-events: none;
          z-index: 0;
        }

        /* Side menu */
        .side-menu {
          position: fixed;
          left: 2rem;
          top: 50%;
          transform: translateY(-50%);
          z-index: 50;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.5rem;
        }
        .menu-icon {
          display: flex;
          flex-direction: column;
          gap: 5px;
          cursor: pointer;
        }
        .menu-icon span {
          display: block;
          height: 1px;
          background: rgba(255,255,255,0.7);
        }
        .menu-icon span:nth-child(1) { width: 24px; }
        .menu-icon span:nth-child(2) { width: 16px; }
        .menu-icon span:nth-child(3) { width: 24px; }
        .vertical-text {
          writing-mode: vertical-lr;
          font-size: 9px;
          letter-spacing: 0.6em;
          font-weight: 300;
          opacity: 0.4;
          text-transform: uppercase;
        }

        /* Fixed first-section hero content */
        .hero-content {
          position: fixed;
          inset: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 1rem;
          z-index: 10;
          pointer-events: none;
          transition: opacity 0.1s linear;
        }

        /* BIG RED title */
        .hero-title {
          font-size: clamp(5rem, 14vw, 10rem);
          font-weight: 900;
          letter-spacing: -0.04em;
          line-height: 1;
          margin: 0 0 1rem;
          color: #ff2020;
          text-shadow:
            0 0 40px rgba(255,32,32,0.6),
            0 0 80px rgba(255,32,32,0.3),
            0 0 160px rgba(255,32,32,0.15);
        }

        .hero-subtitle {
          max-width: 600px;
        }
        .subtitle-line {
          font-size: clamp(1rem, 2vw, 1.4rem);
          font-weight: 300;
          margin: 0.3rem 0;
          opacity: 0.8;
        }

        /* Scroll progress bar */
        .scroll-progress {
          position: fixed;
          bottom: 2rem;
          left: 50%;
          transform: translateX(-50%);
          z-index: 50;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.75rem;
          width: 14rem;
        }
        .scroll-text {
          font-size: 9px;
          letter-spacing: 0.4em;
          font-weight: 700;
          opacity: 0.45;
          text-transform: uppercase;
        }
        .progress-track {
          width: 100%;
          height: 1px;
          background: rgba(255,255,255,0.15);
          overflow: hidden;
        }
        .progress-fill {
          height: 100%;
          background: #ff2020;
          transition: width 0.3s ease-out;
        }
        .section-counter {
          font-family: monospace;
          font-size: 10px;
          letter-spacing: 0.25em;
          opacity: 0.45;
        }

        /* Scroll sections */
        .scroll-sections {
          position: relative;
          z-index: 20;
        }
        .content-section {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 2rem 1rem;
        }
        /* Section titles also red */
        .content-section .hero-title {
          font-size: clamp(4rem, 12vw, 9rem);
        }
      `}</style>

      <div
        ref={containerRef}
        className="hero-container"
        style={{ height: `${(totalSections + 1) * 100}vh` }}
      >
        <canvas ref={canvasRef} className="hero-canvas" />

        {/* Side menu */}
        <div ref={menuRef} className="side-menu" style={{ visibility: 'hidden' }}>
          <div className="menu-icon">
            <span /><span /><span />
          </div>
          <div className="vertical-text">SPACE</div>
        </div>

        {/* Fixed first-section hero — fades out on scroll */}
        <div
          ref={undefined}
          className="hero-content"
          style={{ opacity: heroOpacity }}
        >
          <h1 ref={titleRef} className="hero-title" style={{ visibility: 'hidden' }}>
            {sections[0].title}
          </h1>
          <div ref={subtitleRef} className="hero-subtitle" style={{ visibility: 'hidden' }}>
            <p className="subtitle-line">{sections[0].line1}</p>
            <p className="subtitle-line">{sections[0].line2}</p>
          </div>
        </div>

        {/* Scroll progress */}
        <div ref={scrollProgressRef} className="scroll-progress" style={{ visibility: 'hidden' }}>
          <div className="scroll-text">SCROLL</div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${scrollProgress * 100}%` }} />
          </div>
          <div className="section-counter">
            {String(currentSection + 1).padStart(2,'0')} / {String(totalSections + 1).padStart(2,'0')}
          </div>
        </div>

        {/* Spacer + scroll sections */}
        <div style={{ height: '100vh' }} />
        <div className="scroll-sections">
          {sections.slice(1).map((section, i) => (
            <section key={i} className="content-section">
              <h1 className="hero-title">{section.title}</h1>
              <div className="hero-subtitle">
                <p className="subtitle-line">{section.line1}</p>
                <p className="subtitle-line">{section.line2}</p>
              </div>
            </section>
          ))}
        </div>
      </div>
    </>
  );
};
