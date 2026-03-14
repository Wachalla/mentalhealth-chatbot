import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import * as THREE from "three";
import { isDarkColorScheme, useTheme } from "@/contexts/ThemeContext";

const STARFIELD_VERTEX_SHADER = `
attribute float aSize;
attribute float aPhase;
attribute float aSpeed;
attribute vec2 aVelocity;
attribute float aAlpha;

uniform float uTime;
uniform float uScale;
uniform vec2 uViewport;

varying float vAlpha;

void main() {
  vec3 transformed = position;
  transformed.x = mod(position.x + (uTime * aVelocity.x * aSpeed) + (uViewport.x * 0.5), uViewport.x) - (uViewport.x * 0.5);
  transformed.y = mod(position.y + (uTime * aVelocity.y * aSpeed) + (uViewport.y * 0.5), uViewport.y) - (uViewport.y * 0.5);

  vec4 mvPosition = modelViewMatrix * vec4(transformed, 1.0);
  gl_Position = projectionMatrix * mvPosition;
  gl_PointSize = aSize * uScale * (0.9 + 0.18 * sin((uTime * 0.8) + aPhase));
  vAlpha = aAlpha * (0.68 + 0.32 * sin((uTime * (aSpeed * 1.7)) + aPhase));
}
`;

const STARFIELD_FRAGMENT_SHADER = `
uniform vec3 uColor;

varying float vAlpha;

void main() {
  vec2 centered = gl_PointCoord - vec2(0.5);
  float distanceToCenter = length(centered);
  float glow = smoothstep(0.5, 0.0, distanceToCenter);
  glow *= smoothstep(0.24, 0.0, distanceToCenter) * 0.35 + 0.65;

  gl_FragColor = vec4(uColor, glow * vAlpha);
}
`;

const ShootingStarsOverlay = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const location = useLocation();
  const { colorScheme, overlayEffect } = useTheme();
  const shouldRender = overlayEffect === "shooting-stars" && isDarkColorScheme(colorScheme) && location.pathname !== "/vr";

  useEffect(() => {
    if (!shouldRender || !containerRef.current) {
      return;
    }

    const container = containerRef.current;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const scene = new THREE.Scene();
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "low-power" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    renderer.setClearColor(0x000000, 0);
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.opacity = "0.85";
    container.appendChild(renderer.domElement);

    let viewportWidth = window.innerWidth;
    let viewportHeight = window.innerHeight;

    type StarFieldAssets = {
      count: number;
      color: string;
      geometry: THREE.BufferGeometry;
      material: THREE.ShaderMaterial;
      opacityRange: [number, number];
      points: THREE.Points<THREE.BufferGeometry, THREE.ShaderMaterial>;
      scale: number;
      sizeRange: [number, number];
      speedRange: [number, number];
      velocityXRange: [number, number];
      velocityYRange: [number, number];
    };

    const camera = new THREE.OrthographicCamera(
      -viewportWidth / 2,
      viewportWidth / 2,
      viewportHeight / 2,
      -viewportHeight / 2,
      1,
      1000,
    );
    camera.position.z = 10;

    const buildStarFieldAttributes = (field: Pick<StarFieldAssets, "count" | "opacityRange" | "sizeRange" | "speedRange" | "velocityXRange" | "velocityYRange">) => {
      const positions = new Float32Array(field.count * 3);
      const sizes = new Float32Array(field.count);
      const phases = new Float32Array(field.count);
      const speeds = new Float32Array(field.count);
      const velocities = new Float32Array(field.count * 2);
      const alphas = new Float32Array(field.count);

      for (let index = 0; index < field.count; index += 1) {
        const offset = index * 3;
        positions[offset] = THREE.MathUtils.randFloatSpread(viewportWidth);
        positions[offset + 1] = THREE.MathUtils.randFloatSpread(viewportHeight);
        positions[offset + 2] = 0;

        sizes[index] = THREE.MathUtils.randFloat(field.sizeRange[0], field.sizeRange[1]);
        phases[index] = Math.random() * Math.PI * 2;
        speeds[index] = THREE.MathUtils.randFloat(field.speedRange[0], field.speedRange[1]);
        alphas[index] = THREE.MathUtils.randFloat(field.opacityRange[0], field.opacityRange[1]);

        const velocityOffset = index * 2;
        velocities[velocityOffset] = THREE.MathUtils.randFloat(field.velocityXRange[0], field.velocityXRange[1]);
        velocities[velocityOffset + 1] = THREE.MathUtils.randFloat(field.velocityYRange[0], field.velocityYRange[1]);
      }

      return { alphas, phases, positions, sizes, speeds, velocities };
    };

    const applyStarFieldAttributes = (field: StarFieldAssets) => {
      const { alphas, phases, positions, sizes, speeds, velocities } = buildStarFieldAttributes(field);
      field.geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      field.geometry.setAttribute("aSize", new THREE.BufferAttribute(sizes, 1));
      field.geometry.setAttribute("aPhase", new THREE.BufferAttribute(phases, 1));
      field.geometry.setAttribute("aSpeed", new THREE.BufferAttribute(speeds, 1));
      field.geometry.setAttribute("aVelocity", new THREE.BufferAttribute(velocities, 2));
      field.geometry.setAttribute("aAlpha", new THREE.BufferAttribute(alphas, 1));
    };

    const createStarField = (config: Omit<StarFieldAssets, "geometry" | "material" | "points">) => {
      const geometry = new THREE.BufferGeometry();
      const material = new THREE.ShaderMaterial({
        uniforms: {
          uColor: { value: new THREE.Color(config.color) },
          uScale: { value: config.scale },
          uTime: { value: 0 },
          uViewport: { value: new THREE.Vector2(viewportWidth, viewportHeight) },
        },
        vertexShader: STARFIELD_VERTEX_SHADER,
        fragmentShader: STARFIELD_FRAGMENT_SHADER,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      });
      const points = new THREE.Points(geometry, material);
      const field: StarFieldAssets = { ...config, geometry, material, points };

      applyStarFieldAttributes(field);

      return field;
    };

    // Background distant stars (slower, smaller)
    const backgroundField = createStarField({
      count: prefersReducedMotion ? 120 : 200,
      color: "#e8f4ff",
      opacityRange: [0.3, 0.7],
      scale: 0.6,
      sizeRange: [0.4, 1.2],
      speedRange: [0.1, 0.3],
      velocityXRange: [-4, -1],
      velocityYRange: [-3, -0.8],
    });
    scene.add(backgroundField.points);

    // Main starfield
    const starField = createStarField({
      count: prefersReducedMotion ? 90 : 260,
      color: "#f7fbff",
      opacityRange: [0.4, 1.0],
      scale: prefersReducedMotion ? 1.1 : 1.45,
      sizeRange: prefersReducedMotion ? [1.1, 2.8] : [0.8, 4.8],
      speedRange: prefersReducedMotion ? [0.18, 0.32] : [0.35, 1.2],
      velocityXRange: prefersReducedMotion ? [-6, -2] : [-22, -8],
      velocityYRange: prefersReducedMotion ? [-4, -1.5] : [-16, -5],
    });
    scene.add(starField.points);

    // Glow layer (brighter, larger)
    const glowField = createStarField({
      count: prefersReducedMotion ? 18 : 40,
      color: "#c8e6ff",
      opacityRange: [0.2, 0.5],
      scale: prefersReducedMotion ? 1.6 : 2.1,
      sizeRange: prefersReducedMotion ? [2.8, 4.9] : [3.8, 8.6],
      speedRange: prefersReducedMotion ? [0.14, 0.24] : [0.2, 0.55],
      velocityXRange: prefersReducedMotion ? [-2.5, -1] : [-8, -3],
      velocityYRange: prefersReducedMotion ? [-1.8, -0.7] : [-5.5, -1.5],
    });
    scene.add(glowField.points);

    const hazeGeometry = new THREE.PlaneGeometry(viewportWidth, viewportHeight);
    const hazeMaterial = new THREE.MeshBasicMaterial({
      color: 0x0a1024,
      transparent: true,
      opacity: 0.08,
      depthWrite: false,
    });
    const haze = new THREE.Mesh(hazeGeometry, hazeMaterial);
    haze.position.z = -5;
    scene.add(haze);

    type ShootingStarState = {
      delay: number;
      duration: number;
      elapsed: number;
      mesh: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
      velocityX: number;
      velocityY: number;
    };

    const streakGeometry = new THREE.PlaneGeometry(280, 3.2);
    const shootingStars: ShootingStarState[] = prefersReducedMotion
      ? []
      : Array.from({ length: 8 }, () => {
          const material = new THREE.MeshBasicMaterial({
            color: 0xb9d8ff,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
            side: THREE.DoubleSide,
          });
          const mesh = new THREE.Mesh(streakGeometry, material);
          mesh.visible = false;
          scene.add(mesh);

          return {
            delay: 0,
            duration: 0,
            elapsed: 0,
            mesh,
            velocityX: 0,
            velocityY: 0,
          };
        });

    const scheduleShootingStar = (shootingStar: ShootingStarState, immediate = false) => {
      shootingStar.delay = immediate ? Math.random() * 0.6 : 0.6 + Math.random() * 2.0;
      shootingStar.duration = 0.9 + Math.random() * 0.4;
      shootingStar.elapsed = 0;
      shootingStar.velocityX = 680 + Math.random() * 320;
      shootingStar.velocityY = -(340 + Math.random() * 180);
      shootingStar.mesh.visible = false;
      shootingStar.mesh.scale.set(1.0 + Math.random() * 1.4, 1, 1);
      shootingStar.mesh.rotation.z = Math.atan2(shootingStar.velocityY, shootingStar.velocityX);
      shootingStar.mesh.position.set(
        -viewportWidth / 2 + Math.random() * viewportWidth * 0.7,
        viewportHeight / 2 + 60 + Math.random() * viewportHeight * 0.35,
        0,
      );
      shootingStar.mesh.material.opacity = 0;
    };

    shootingStars.forEach((shootingStar, index) => {
      scheduleShootingStar(shootingStar, index === 0);
    });

    const handleResize = () => {
      viewportWidth = window.innerWidth;
      viewportHeight = window.innerHeight;
      camera.left = -viewportWidth / 2;
      camera.right = viewportWidth / 2;
      camera.top = viewportHeight / 2;
      camera.bottom = -viewportHeight / 2;
      camera.updateProjectionMatrix();
      renderer.setSize(viewportWidth, viewportHeight);
      starField.material.uniforms.uViewport.value.set(viewportWidth, viewportHeight);
      glowField.material.uniforms.uViewport.value.set(viewportWidth, viewportHeight);
      backgroundField.material.uniforms.uViewport.value.set(viewportWidth, viewportHeight);
      haze.geometry.dispose();
      haze.geometry = new THREE.PlaneGeometry(viewportWidth, viewportHeight);
      applyStarFieldAttributes(starField);
      applyStarFieldAttributes(glowField);
      applyStarFieldAttributes(backgroundField);
      shootingStars.forEach((shootingStar) => scheduleShootingStar(shootingStar, true));
    };

    handleResize();
    window.addEventListener("resize", handleResize);

    let animationFrame = 0;
    let previousTime = performance.now();

    const animate = (time: number) => {
      const delta = Math.min(0.033, (time - previousTime) / 1000);
      previousTime = time;
      const elapsed = time * 0.001;

      starField.material.uniforms.uTime.value = elapsed;
      glowField.material.uniforms.uTime.value = elapsed * 0.82;
      backgroundField.material.uniforms.uTime.value = elapsed * 0.6;

      shootingStars.forEach((shootingStar) => {
        if (shootingStar.delay > 0) {
          shootingStar.delay -= delta;
          if (shootingStar.delay <= 0) {
            shootingStar.mesh.visible = true;
          }
          return;
        }

        shootingStar.elapsed += delta;
        shootingStar.mesh.position.x += shootingStar.velocityX * delta;
        shootingStar.mesh.position.y += shootingStar.velocityY * delta;

        const progress = shootingStar.elapsed / shootingStar.duration;
        const fadeIn = Math.min(1, progress / 0.08);
        const fadeOut = progress > 0.7 ? Math.max(0, 1 - (progress - 0.7) / 0.3) : 1;
        shootingStar.mesh.material.opacity = 0.95 * fadeIn * fadeOut;

        if (
          progress >= 1 ||
          shootingStar.mesh.position.x > viewportWidth / 2 + 350 ||
          shootingStar.mesh.position.y < -viewportHeight / 2 - 280
        ) {
          scheduleShootingStar(shootingStar);
        }
      });

      renderer.render(scene, camera);
      animationFrame = window.requestAnimationFrame(animate);
    };

    animationFrame = window.requestAnimationFrame(animate);

    return () => {
      window.cancelAnimationFrame(animationFrame);
      window.removeEventListener("resize", handleResize);
      backgroundField.geometry.dispose();
      backgroundField.material.dispose();
      starField.geometry.dispose();
      starField.material.dispose();
      glowField.geometry.dispose();
      glowField.material.dispose();
      haze.geometry.dispose();
      haze.material.dispose();
      streakGeometry.dispose();
      shootingStars.forEach((shootingStar) => {
        shootingStar.mesh.material.dispose();
      });
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, [shouldRender]);

  if (!shouldRender) {
    return null;
  }

  return <div ref={containerRef} className="pointer-events-none absolute inset-0 z-0 overflow-hidden" aria-hidden="true" />;
};

export default ShootingStarsOverlay;
