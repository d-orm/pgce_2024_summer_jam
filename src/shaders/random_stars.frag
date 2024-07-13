#version 300 es
precision highp float;
precision highp int;

#include "uniforms"
#include "iResolution"

in vec2 fragCoord;
in vec2 out_pos;
in float out_bright;
out vec4 fragColor;

const vec2 smooth_edges = vec2(0.02); 

float rect_falloff(vec2 uv, vec2 rect_min, vec2 rect_max) {
    vec2 dist_min = uv - rect_min;
    vec2 dist_max = rect_max - uv;
    float dist = min(min(dist_min.x, dist_min.y), min(dist_max.x, dist_max.y));
    return 1.0 - smoothstep(0.0, smooth_edges.x, dist);
}

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
    
    vec2 pos = out_pos / iResolution.xy;
    uv = (uv - pos) * (2.0 * (cos(iTime) - 11.5)); 

    float radius = 25.25 * out_bright;
    float anim = sin(iTime * 11.0) * 0.1 + 1.0;

    vec2 rect_min = vec2(constellationRect[0], constellationRect[1]) / iResolution;
    vec2 rect_max = vec2(constellationRect[0] + constellationRect[2], constellationRect[1] + constellationRect[3]) / iResolution;

    float visibility = rect_falloff(uv, rect_min, rect_max);

    color = star(uv, anim, radius) * vec3(0.0514 + out_bright) * visibility;

    fragColor = vec4(color, color);
}
