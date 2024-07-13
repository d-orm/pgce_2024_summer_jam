import asyncio
import struct

import pygame
import zengl

import src.constants as constants
from src.game import Game
from src.shader_pipeline import ShaderPipeline


class App:
    def __init__(self):
        self.screen_size = self.screen_w, self.screen_h = constants.SCREEN_SIZE
        pygame.init()
        self.screen = pygame.display.set_mode(
            self.screen_size, pygame.OPENGL | pygame.DOUBLEBUF
        ).convert_alpha()
        self.ctx = zengl.context()
        pygame.display.set_caption("Constellations")
        self.clock = pygame.time.Clock()
        self.game = Game(self)
        self.game.reset_level()
        self.game.init_level()
        uniforms_map = {
            "iTime": {
                "value": lambda: struct.pack("f", self.elapsed_time),
                "glsl_type": "float",
            },
            "numRandomStars": {
                "value": lambda: struct.pack("i", self.game.stars.num_random_points),
                "glsl_type": "int",
            },
            "constellationRect": {
                "value": lambda: struct.pack(
                    "ffff", *self.game.stars.constellation_rect
                ),
                "glsl_type": "vec4",
            },
        }
        self.uniforms, self.ufs_size, self.ufs_includes = self.pack_uniforms(
            uniforms_map
        )
        self.uniform_buffer = self.ctx.buffer(size=self.ufs_size)
        self.ctx.includes["uniforms"] = self.ufs_includes["uniforms"]
        vec2_screen_size_str = f"vec2({self.screen_size[0]}.0, {self.screen_size[1]}.0)"
        self.ctx.includes["iResolution"] = (
            f"const vec2 iResolution = {vec2_screen_size_str};"
        )
        self.space_bg_shader = ShaderPipeline(
            self, self.uniform_buffer, frag_shader_id="space_bg", has_tex=False
        )
        self.aurora_shader = ShaderPipeline(
            self, self.uniform_buffer, frag_shader_id="aurora", has_tex=False
        )
        self.constellation_shader = ShaderPipeline(
            self,
            self.uniform_buffer,
            vert_shader_id="constellation",
            frag_shader_id="constellation",
            has_tex=False,
            instance_buffer_size=64000,
            instance_buffer_layout=("2f 1f /i", 0, 1),
            blend={"enable": True, "src_color": "one", "dst_color": "one"},
        )
        self.random_stars_shader = ShaderPipeline(
            self,
            self.uniform_buffer,
            vert_shader_id="constellation",
            frag_shader_id="random_stars",
            has_tex=False,
            instance_buffer_size=64000,
            instance_buffer_layout=("2f 1f /i", 0, 1),
        )
        self.screen_shader = ShaderPipeline(self, self.uniform_buffer)
        pygame.mixer.music.load(constants.MUSIC_PATH)
        self.running = True

    def render(self):
        self.update_uniforms()
        self.ctx.new_frame()

        self.aurora_shader.render()
        self.space_bg_shader.render()

        points = self.game.stars.const_points_and_brightnesses
        num_points = len(points) * 3
        self.constellation_shader.render(
            instance_data=struct.pack(
                "f" * num_points, *[item for sublist in points for item in sublist]
            ),
            instance_count=num_points // 3,
        )

        rand_points = self.game.stars.rand_points_and_brightnesses
        num_rand_points = len(rand_points) * 3
        self.random_stars_shader.render(
            instance_data=struct.pack(
                "f" * num_rand_points,
                *[item for sublist in rand_points for item in sublist],
            ),
            instance_count=num_rand_points // 3,
        )

        self.screen_shader.render(self.screen)
        self.ctx.end_frame()
        pygame.display.flip()

    async def run(self):
        while self.running:
            self.elapsed_time = pygame.time.get_ticks() / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    self.running = False
                self.game.handle_events(event)
            self.game.update()
            self.game.draw(self.screen)
            self.render()
            self.clock.tick()
            await asyncio.sleep(0)

    def update_uniforms(self):
        for uniform in self.uniforms.values():
            self.uniform_buffer.write(uniform["value"](), offset=uniform["offset"])

    @staticmethod
    def pack_uniforms(uniforms_map: dict) -> tuple[dict, int, dict]:
        uniforms = {}
        layout = ""
        offset = 0
        for uf_name, uf_data in uniforms_map.items():
            if uf_data["glsl_type"] == "float":
                size = 4  # Size of a float in bytes
                align = 4
            elif uf_data["glsl_type"] == "int":
                size = 4
                align = 4
            elif uf_data["glsl_type"] == "vec2":
                size = 8  # 2 floats
                align = 8
            elif uf_data["glsl_type"] == "vec3":
                size = 12  # 3 floats, but aligned as vec4 in std140 layout
                align = 16
            elif uf_data["glsl_type"] == "vec4":
                size = 16  # 4 floats
                align = 16
            elif uf_data["glsl_type"] == "mat4":
                size = 64  # 4x4 floats
                align = 16  # aligned as vec4 in std140 layout
            else:
                raise ValueError(f"Unknown GLSL type: {uf_data['glsl_type']}")

            # Add padding for alignment
            if offset % align != 0:
                offset += align - (offset % align)

            uniforms[uf_name] = {"value": uf_data["value"], "offset": offset}
            offset += size
            layout += f"{uf_data['glsl_type']} {uf_name};\n"

        includes = f"""
                layout (std140) uniform Common {{{layout if uniforms else 'float dummy;'}}};
            """
        buffer_size = 16 + offset
        return uniforms, buffer_size, {"uniforms": includes.strip()}
