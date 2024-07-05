#version 300 es
precision highp float;
precision highp int;

#include "uniforms"
#include "iResolution"

layout(location = 0) in vec2 in_pos;
layout(location = 1) in float in_brightness;

vec2 vertex[4] = vec2[](
    vec2(-1.0, -1.0),
    vec2(-1.0, 1.0),
    vec2(1.0, -1.0),
    vec2(1.0, 1.0)
);

out vec2 fragCoord;
out vec2 out_pos;
out float out_bright;

void main() {
    fragCoord = vertex[gl_VertexID] * vec2(0.5, -0.5) + 0.5;
    gl_Position = vec4(vertex[gl_VertexID], 0.0, 1.0);
    out_pos = in_pos;
    out_bright = in_brightness;
}