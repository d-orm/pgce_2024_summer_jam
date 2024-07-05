from typing import TYPE_CHECKING

import zengl

if TYPE_CHECKING:
    from src.app import App
    import pygame


class ShaderPipeline:
    def __init__(
            self, 
            app: "App", 
            uniforms_buffer: zengl.Buffer, 
            vert_shader_id: str="default", 
            frag_shader_id: str="default", 
            has_tex: bool=True,
            instance_buffer_size: int | None=None,
            instance_buffer_layout: tuple[str, int] | None=None,
            blend: dict={
                'enable': True, 
                'src_color': "src_alpha", 
                'dst_color': "one_minus_src_alpha"
            },
        ):
        self.app = app
        self.ctx = app.ctx
        self.has_tex = has_tex
        self.blend = blend
        self.image = self.ctx.image(self.app.screen_size, 'rgba8unorm')
        self.uniform_buffer = uniforms_buffer
        self.instance_buffer = self.ctx.buffer(size=instance_buffer_size) if instance_buffer_size else None
        layout, resources = self.get_resources_and_layout()

        self.pipeline = self.ctx.pipeline(
            vertex_shader=self.load_shader_src(f'{vert_shader_id}.vert'),
            fragment_shader=self.load_shader_src(f'{frag_shader_id}.frag'),
            layout=layout,
            resources=resources,
            framebuffer=None,
            topology='triangle_strip',
            viewport=(0, 0, *self.app.screen_size),
            vertex_buffers=[] if not instance_buffer_size else zengl.bind(self.instance_buffer, *instance_buffer_layout),
            vertex_count=4,
            blend=self.blend,
            instance_count=1 if not instance_buffer_size else 1
        )
    
    def get_resources_and_layout(self):
        layout = [{'name': 'Common', 'binding': 0}]
        resources = [{'type': 'uniform_buffer', 'binding': 0, 'buffer': self.uniform_buffer}]
        if self.has_tex:
            layout.append({'name': 'Texture', 'binding': 0})
            resources.append(
                {
                    'type': 'sampler',
                    'binding': 0,
                    'image': self.image,
                    'min_filter': 'nearest',
                    'mag_filter': 'nearest',
                    'wrap_x': 'clamp_to_edge',
                    'wrap_y': 'clamp_to_edge',
                }
            )
        return layout, resources

    def render(self, screen: "pygame.Surface | None"=None, instance_data: bytes | None=None, instance_count: int =1):
        if instance_data:
            self.instance_buffer.write(instance_data)
            self.pipeline.instance_count = instance_count
        if screen:
            screen_buffer = screen.get_view('0').raw
            self.image.write(screen_buffer)
        self.pipeline.render()

    @staticmethod
    def load_shader_src(shader_name: str) -> str:
        with open(f"src/shaders/{shader_name}") as f:
            return f.read()
        
