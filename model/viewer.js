import * as THREE from 'three';
import { OrbitControls } from './vendor/OrbitControls.js';

const data = JSON.parse(document.querySelector('#model-data').textContent);
const canvas = document.querySelector('canvas');
const status = document.querySelector('#status');
try {
  const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#eae7df');
  const camera = new THREE.PerspectiveCamera(38, 1, .1, 600);
  camera.up.set(0,0,1);
  const controls = new OrbitControls(camera, canvas);
  let dirty=true;
  controls.addEventListener("change",()=>{dirty=true});
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI*.49;
  controls.minDistance = 12;
  controls.maxDistance = 230;
  scene.add(new THREE.HemisphereLight(0xfff8e8,0x797d6d,1.7));
  const sun = new THREE.DirectionalLight(0xfff4d9,2.4);
  sun.position.set(40,-20,65);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048,2048);
  Object.assign(sun.shadow.camera,{left:-45,right:45,top:45,bottom:-45,near:1,far:130});
  sun.shadow.normalBias = .1;
  sun.shadow.bias = -.0002;
  sun.target.position.set(17,30,0);
  scene.add(sun,sun.target);
  const building = new THREE.Group();
  building.position.set(5,20,0);
  scene.add(building);
  const cutPlane = new THREE.Plane(new THREE.Vector3(0,0,-1),12.25);
  const meshes = [];
  for (const part of data.parts) {
    if(part.category==='Room zone') continue;
    let geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(part.vertices.flat(),3));
    geometry.setIndex(part.faces.flat());
    geometry = geometry.toNonIndexed();
    geometry.computeVertexNormals();
    const glass = part.category==='Window';
    const color = new THREE.Color((part.color[0]<<16)+(part.color[1]<<8)+part.color[2]);
    const material = new THREE.MeshStandardMaterial({color,roughness:glass?.2:.78,metalness:glass?.15:.02,side:THREE.DoubleSide});
    const mesh = new THREE.Mesh(geometry,material);
    mesh.userData = part;
    mesh.originalGeometry = geometry;
    mesh.cutGeometries = {};
    mesh.castShadow = !glass;
    mesh.receiveShadow = true;
    building.add(mesh);
    meshes.push(mesh);
  }
  const context = new THREE.Group();
  scene.add(context);
  for(const part of data.context){
    let geometry;
    if(part.vertices){
      geometry=new THREE.BufferGeometry();
      geometry.setAttribute('position',new THREE.Float32BufferAttribute(part.vertices.flat(),3));
      geometry.setIndex(part.faces.flat());geometry=geometry.toNonIndexed();geometry.computeVertexNormals();
    }else geometry=new THREE.BoxGeometry(...part.size);
    const mesh = new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:part.color,roughness:1,side:THREE.DoubleSide}));
    if(part.center) mesh.position.set(...part.center);
    mesh.receiveShadow=true;mesh.castShadow=true;mesh.name=part.name;context.add(mesh);
  }
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(500,500),new THREE.MeshStandardMaterial({color:'#deddd2',roughness:1}));
  ground.position.z=-.55;ground.receiveShadow=true;scene.add(ground);
  const presets={
    yard:{pos:[61,-17,31],target:[18,29,7],note:'The yard elevation, east balconies and south stair.'},
    alley:{pos:[-35,-14,29],target:[17,29,7],note:'The alley elevation: garage door west, apartment window above.'},
    level2:{pos:[44,-7,53],target:[17,30,9.2],note:'Apartment · direct laundry access and an open route past the peninsula.'},
    level1:{pos:[45,-5,46],target:[17,30,1.5],note:'Garage · 23 ft clear length, 39 in hall and a separate garden office.'},
    site:{pos:[158,-120,143],target:[67,23,0],note:'Site study · existing house and replacement shed are approximate masses.'}
  };
  let current='yard';
  const roof=document.querySelector('#roof'), furniture=document.querySelector('#furniture');
  function visibility(){
    dirty=true;
    const cut=current==='level1'||current==='level2';
    cutPlane.constant=current==='level1'?3.5:12.25;
    for(const mesh of meshes){
      const p=mesh.userData;
      const isFurniture=['Furniture','Vehicle'].includes(p.category);
      let visible=p.category!=='Vehicle';
      if(p.category==='Roof') visible=roof.checked&&!cut;
      if(isFurniture&&!furniture.checked) visible=false;
      if(cut){
        if(p.level!==(current==='level1'?'Level 1':'Level 2')) visible=false;
        if(p.category==='Roof') visible=false;
      }
      mesh.visible=visible;
      mesh.geometry=mesh.originalGeometry;
      if(cut&&!isFurniture&&p.shape==='box'&&!p.rotate_x){
        if(!mesh.cutGeometries[current]){
          const low=p.center[2]-p.size[2]/2;
          const height=Math.max(.001,Math.min(p.size[2],cutPlane.constant-low));
          const cap=new THREE.BoxGeometry(p.size[0],p.size[1],height);
          cap.translate(p.center[0],p.center[1],low+height/2);
          mesh.cutGeometries[current]=cap;
        }
        if(p.center[2]-p.size[2]/2>=cutPlane.constant) mesh.visible=false;
        mesh.geometry=mesh.cutGeometries[current];
        mesh.material.clippingPlanes=[];
      }else mesh.material.clippingPlanes=cut&&!isFurniture?[cutPlane]:[];
    }
    for(const mesh of context.children) mesh.visible=current==='site'||['Lot','Alley'].includes(mesh.name);
    roof.disabled=cut;
  }
  function setView(view){
    current=presets[view]?view:'yard';
    const preset=presets[current];
    camera.position.set(...preset.pos);controls.target.set(...preset.target);controls.update();
    document.querySelector('#view-note').textContent=preset.note;
    document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===current)));
    visibility();
  }
  document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>{setView(button.dataset.view);history.replaceState(null,'','#'+current)}));
  roof.addEventListener('change',visibility);furniture.addEventListener('change',visibility);
  document.querySelector('#reset').addEventListener('click',()=>setView(current));
  function resize(){dirty=true;renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.zoom=Math.min(1,camera.aspect/1.2);camera.updateProjectionMatrix()}
  addEventListener('resize',resize);resize();setView(location.hash.slice(1));
  status.hidden=true;
  renderer.setAnimationLoop(()=>{if(!document.hidden){controls.update();if(dirty){renderer.render(scene,camera);dirty=false}}});
} catch(error){
  console.error(error);status.hidden=true;document.querySelector('#fallback').hidden=false;
  document.querySelector('aside').hidden=true;
}
