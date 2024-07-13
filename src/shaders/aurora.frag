#version 300 es
precision highp float;
precision highp int;

// adapted from https://www.shadertoy.com/view/MlSfzz

#define nsin(x) (sin(x) * 0.5 + 0.5)

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;



float rand(vec2 uv) {
    const float a = 12.9898;
    const float b = 78.233;
    const float c = 43758.5453;
    float dt = dot(uv, vec2(a, b));
    float sn = mod(dt, 3.1415);
    return fract(sin(sn) * c);
}

void draw_stars(inout vec4 color, vec2 uv) {
    float t = sin(iTime * 2.0 * rand(-uv)) * 0.5 + 0.5;
    //color += step(0.99, stars) * t;
    color += smoothstep(0.975, 1.0, rand(uv)) * t;
}
void main() {
    vec2 uv = fragCoord;
    uv.y = 1.0 - uv.y;
    vec4 color = vec4(0.0);
    
    const vec4 aurora_color_a = vec4(0.0, 1.2, 0.5, 1.0);
    const vec4 aurora_color_b = vec4(0.0, 0.4, 0.6, 1.0);
    
    float t = nsin(-iTime + uv.x * 100.0) * 0.075 + nsin(iTime + uv.x * distance(uv.x, 0.5) * 100.0) * 0.1 - 0.5;
    t = 1.0 - smoothstep(uv.y - 4.0, uv.y * 2.0, t);
    
    vec4 final_color = mix(aurora_color_a, aurora_color_b, clamp(1.0 - uv.y * t, 0.0, 1.0));
    final_color += final_color * final_color;
    color += final_color * t * (t + 0.5) * 0.75;
    draw_stars(color, uv);
    fragColor = color;
}