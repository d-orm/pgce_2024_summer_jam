#version 300 es
precision highp float;
precision highp int;

// adapted from https://www.youtube.com/watch?v=rvDo9LvfoVE

#include "uniforms"
#include "iResolution"

in vec2 fragCoord;
out vec4 fragColor;

const float NUM_OF_LAYERS = 2.0;
const float TWO_PI = 6.28318530718;
const vec2 HASH_SCALE = vec2(123.34, 456.21);
const float HASH_OFFSET = 45.32;
const float STAR_FLARE_SCALE = 1000.0;
const float STAR_FLARE_INTENSITY = 0.3;
const float ROTATION_ANGLE = 3.1415 / 4.0;
const vec2 STAR_COLOR_SCALE = vec2(2345.2, 125.2);
const vec3 STAR_BASE_COLOR = vec3(0.2, 0.3, 0.9);
const float STAR_SIZE_SCALE = 34.32;
const vec2 STAR_COLOR_MODIFIER = vec2(1.0, 0.85);
const vec2 STAR_COLOR_OFFSET = vec2(0.2, 0.1);
const float TIME_SCALE = 0.5;
const vec2 UV_SCALE = vec2(20.0, 0.5);
const float UV_OFFSET = 453.2;
const float STAR_MOVEMENT_SPEED = 0.025;

mat2 rotate(float angle){
    float s = sin(angle), c = cos(angle);
    return mat2(c, -s, s, c);
}

float hash21(vec2 p){ 
    p = fract(p * HASH_SCALE);
    p += dot(p, p + HASH_OFFSET);
    return fract(p.x * p.y);
}

float generateStar(vec2 uv, float flare){
    float distance = length(uv);
    float intensity = 0.05 / distance;
    
    float rays = max(0.0, 1.0 - abs(uv.x * uv.y * STAR_FLARE_SCALE));
    intensity += rays * flare;
    
    uv *= rotate(ROTATION_ANGLE);
    
    rays = max(0.0, 1.0 - abs(uv.x * uv.y * STAR_FLARE_SCALE));
    intensity += rays * STAR_FLARE_INTENSITY * flare;
    
    intensity *= smoothstep(1.0, 0.2, distance);
    
    return intensity;
}

vec3 generateStarLayer(vec2 uv){
    vec3 color = vec3(0);
    
    vec2 gridPos = fract(uv) - 0.5;
    vec2 cellId = floor(uv);
    
    for(int y = -1; y <= 1; y++){
        for(int x = -1; x <= 1; x++){
            vec2 offset = vec2(x, y);
            
            float noise = hash21(cellId + offset);
            float size = fract(noise * STAR_SIZE_SCALE);
            float star = generateStar(gridPos - offset - vec2(noise, fract(noise * 34.0)) + 0.5, smoothstep(0.8, 1.0, size));
            
            vec3 starColor = sin(STAR_BASE_COLOR * fract(noise * STAR_COLOR_SCALE.x) * STAR_COLOR_SCALE.y) * 0.5 + 0.5;
            starColor *= vec3(1.0 - STAR_COLOR_OFFSET.x * size, STAR_COLOR_MODIFIER.y - STAR_COLOR_OFFSET.y * size, 1.0 + size);
            
            star *= sin(iTime * TIME_SCALE + noise * TWO_PI) * 0.4 + 1.0;
            
            color += star * size * starColor;
        }
    }
    
    return color;
}

void main()
{
    vec2 uv = fragCoord;
    float time = iTime * STAR_MOVEMENT_SPEED;
    uv *= rotate(time);
    
    vec3 color = vec3(0);
    for(float i = 0.0; i < 1.0; i += 1.0 / NUM_OF_LAYERS) {
        float depth = fract(i + time);
        float scale = mix(UV_SCALE.x, UV_SCALE.y, depth);
        
        float opacity = depth * smoothstep(1.0, 0.9, depth);
        color += generateStarLayer(uv * scale + i * UV_OFFSET) * opacity; 
    }
    
    fragColor = vec4(color, color);
}
