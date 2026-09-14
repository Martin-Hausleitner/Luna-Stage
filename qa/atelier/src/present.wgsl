@group(0) @binding(0) var hdr:texture_2d<f32>;
@vertex fn vs(@builtin(vertex_index) i:u32)->@builtin(position) vec4f{var p=array<vec2f,3>(vec2f(-1,-1),vec2f(3,-1),vec2f(-1,3));return vec4f(p[i],0,1);}
@fragment fn fs(@builtin(position) p:vec4f)->@location(0) vec4f{let uv=p.xy/vec2f(textureDimensions(hdr))*2.-1.;let x=max(textureLoad(hdr,vec2i(p.xy),0).rgb,vec3f(0));let a=x*(2.51*x+.03);let b=x*(2.43*x+.59)+.14;let c=pow(clamp(a/b,vec3f(0),vec3f(1)),vec3f(1./2.2));return vec4f(c*(1.-.033*dot(uv,uv)),1.);}
