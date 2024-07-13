#version 300 es
precision highp float;
precision highp int;

#include "uniforms"
#include "iResolution"

in vec2 fragCoord;
in vec2 out_pos;
in float out_bright;
out vec4 fragColor;

float star(vec2 uv, float anim, float radius)
{
    // adapted from https://www.shadertoy.com/view/4tyfWy
    
    uv = abs(uv);
    
    vec2 uv_yx = uv.yx;
    vec2 uv_div = uv.xy / uv_yx;
    vec2 pos = min(uv_div, vec2(anim));
    
    float p = 2.0 - (pos.x + pos.y);
    float p2 = p * p;
    float star_value = (2.0 + p * (p2 - 1.5)) / (uv.x + uv.y);
    
    float dist_squared = dot(uv, uv);
    float radius_half = radius * 0.5;
    float radius_half_squared = radius_half * radius_half;
    float radius_squared = radius * radius;
    
    float falloff = smoothstep(radius_squared, radius_half_squared, dist_squared);
    
    return star_value * falloff;
}

void main()
{
    vec2 uv = fragCoord;
    vec3 color = vec3(0.0);
    vec2 pos = out_pos;
    pos /= iResolution.xy;
    uv -= pos;
    uv *= 2.0 * ( cos(iTime * 1.0) -11.5); // scale
    float radius = 15.25 * out_bright;
    float anim = sin(iTime * 11.0) * 0.1 + 1.0;  // anim between 0.9 - 1.1 
    color = star(uv, anim, radius) * vec3(0.0214 + out_bright);

   
    fragColor = vec4(color, color);
}