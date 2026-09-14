struct Obj {pos:vec4f,row0:vec4f,row1:vec4f,row2:vec4f,color:vec4f,surf:vec4f,flags:vec4f,dim:vec4f};
struct Shadow {origin:vec4f,right:vec4f,up:vec4f,forward:vec4f};
@group(0) @binding(0) var<storage,read> objects:array<Obj>;
@group(0) @binding(1) var<uniform> s:Shadow;
@vertex fn vs(@location(0) q:vec3f,@location(1) normal:vec3f,@location(2) id:u32)->@builtin(position) vec4f{
let o=objects[id];let a=o.row0.xyz;let b=o.row1.xyz;let c=o.row2.xyz;let inv=1./dot(a,cross(b,c));let p=o.pos.xyz+(cross(b,c)*q.x+cross(c,a)*q.y+cross(a,b)*q.z)*inv;let d=p-s.origin.xyz;
if(o.surf.z>0.){return vec4f(0,0,2,1);}return vec4f(dot(d,s.right.xyz)/s.origin.w,dot(d,s.up.xyz)/s.right.w,dot(d,s.forward.xyz)/s.up.w,1.);
}
