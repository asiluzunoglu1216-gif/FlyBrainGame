"""Low-Poly 3D Drosophila (Fruit Fly) Model Generator for Panda3D.

Constructs an anatomically recognizable adult Drosophila melanogaster:
- Red compound eyes (iconic wild-type ruby/red eyes)
- Amber/brown thorax
- Segmented abdomen with dark stripes
- Translucent flapping wings with dynamic wingbeat animation
"""
from __future__ import annotations

import math
from panda3d.core import (
    NodePath, Geom, GeomNode, GeomVertexData, GeomVertexFormat,
    GeomVertexWriter, GeomTriangles, Vec3, Vec4, TransparencyAttrib
)


def create_cube_geom(size_x: float, size_y: float, size_z: float, color: Vec4) -> GeomNode:
    """Creates a colored box GeomNode centered at origin."""
    vdata = GeomVertexData("cube_vdata", GeomVertexFormat.get_v3c4(), Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    vcolor = GeomVertexWriter(vdata, "color")

    hx, hy, hz = size_x * 0.5, size_y * 0.5, size_z * 0.5

    # 8 corners
    corners = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy,  hz), (hx, -hy,  hz), (hx, hy,  hz), (-hx, hy,  hz)
    ]

    for c in corners:
        vertex.addData3f(*c)
        vcolor.addData4f(color)

    # 6 faces (2 triangles each)
    faces = [
        (0, 1, 2), (0, 2, 3),  # bottom
        (4, 6, 5), (4, 7, 6),  # top
        (0, 5, 1), (0, 4, 5),  # front (-y)
        (3, 2, 6), (3, 6, 7),  # back (+y)
        (0, 3, 7), (0, 7, 4),  # left (-x)
        (1, 5, 6), (1, 6, 2)   # right (+x)
    ]

    triangles = GeomTriangles(Geom.UHStatic)
    for f in faces:
        triangles.addVertices(f[0], f[1], f[2])

    geom = Geom(vdata)
    geom.addPrimitive(triangles)
    node = GeomNode("cube_geom")
    node.addGeom(geom)
    return node


def create_wing_geom(length: float, width: float) -> GeomNode:
    """Creates a thin, translucent wing surface."""
    vdata = GeomVertexData("wing_vdata", GeomVertexFormat.get_v3c4(), Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    vcolor = GeomVertexWriter(vdata, "color")

    wing_color = Vec4(0.85, 0.92, 1.0, 0.65)  # Translucent light blue-white

    # Wing outline (elongated oval approximation)
    pts = [
        (0.0, 0.0, 0.0),                # base
        (-width * 0.4, length * 0.4, 0.0),
        (-width * 0.5, length * 0.7, 0.0),
        (0.0, length, 0.0),              # tip
        (width * 0.5, length * 0.7, 0.0),
        (width * 0.4, length * 0.4, 0.0),
    ]

    for p in pts:
        vertex.addData3f(*p)
        vcolor.addData4f(wing_color)

    triangles = GeomTriangles(Geom.UHStatic)
    # Fan from base
    triangles.addVertices(0, 1, 2)
    triangles.addVertices(0, 2, 3)
    triangles.addVertices(0, 3, 4)
    triangles.addVertices(0, 4, 5)
    # Double-sided
    triangles.addVertices(0, 2, 1)
    triangles.addVertices(0, 3, 2)
    triangles.addVertices(0, 4, 3)
    triangles.addVertices(0, 5, 4)

    geom = Geom(vdata)
    geom.addPrimitive(triangles)
    node = GeomNode("wing_geom")
    node.addGeom(geom)
    return node


class FlyModel:
    """Hierarchical low-poly Drosophila model with animated wings."""

    def __init__(self, parent: NodePath, scale: float = 1.0):
        self.root = parent.attachNewNode("FlyModelRoot")
        self.root.setScale(scale)

        # Colors
        c_thorax = Vec4(0.62, 0.44, 0.24, 1.0)     # Amber brown
        c_abdomen = Vec4(0.45, 0.32, 0.18, 1.0)    # Striped brown-tan
        c_head = Vec4(0.55, 0.38, 0.20, 1.0)
        c_eye = Vec4(0.88, 0.12, 0.12, 1.0)       # Iconic wild-type red eyes
        c_leg = Vec4(0.20, 0.15, 0.10, 1.0)

        # 1. Thorax (Center body)
        self.thorax = self.root.attachNewNode(create_cube_geom(1.4, 2.0, 1.2, c_thorax))
        self.thorax.setPos(0.0, 0.0, 0.0)

        # 2. Head
        self.head = self.root.attachNewNode(create_cube_geom(1.2, 1.0, 1.0, c_head))
        self.head.setPos(0.0, 1.4, 0.1)

        # 3. Large Red Compound Eyes (Left & Right)
        self.eye_l = self.head.attachNewNode(create_cube_geom(0.5, 0.7, 0.7, c_eye))
        self.eye_l.setPos(-0.55, 0.1, 0.1)

        self.eye_r = self.head.attachNewNode(create_cube_geom(0.5, 0.7, 0.7, c_eye))
        self.eye_r.setPos(0.55, 0.1, 0.1)

        # 4. Antennae with sensory aristae (Front of head)
        c_ant = Vec4(0.35, 0.25, 0.15, 1.0)
        self.antenna_l = self.head.attachNewNode(create_cube_geom(0.12, 0.35, 0.12, c_ant))
        self.antenna_l.setPos(-0.25, 0.55, 0.25)
        self.antenna_l.setHpr(-20, 25, 0)

        self.antenna_r = self.head.attachNewNode(create_cube_geom(0.12, 0.35, 0.12, c_ant))
        self.antenna_r.setPos(0.25, 0.55, 0.25)
        self.antenna_r.setHpr(20, 25, 0)

        # 5. Articulated Proboscis (Ventral head, extends for feeding)
        c_prob = Vec4(0.70, 0.52, 0.32, 1.0)
        c_labellum = Vec4(0.85, 0.30, 0.30, 1.0)
        self.proboscis_pivot = self.head.attachNewNode("ProboscisPivot")
        self.proboscis_pivot.setPos(0.0, 0.25, -0.45)
        self.proboscis_pivot.setP(35.0)  # Tucked under head when retracted

        self.proboscis_stem = self.proboscis_pivot.attachNewNode(create_cube_geom(0.25, 0.25, 0.65, c_prob))
        self.proboscis_stem.setPos(0.0, 0.0, -0.32)

        self.labellum = self.proboscis_stem.attachNewNode(create_cube_geom(0.40, 0.35, 0.20, c_labellum))
        self.labellum.setPos(0.0, 0.05, -0.35)

        # 6. Abdomen (Segmented, posterior)
        self.abdomen = self.root.attachNewNode(create_cube_geom(1.3, 2.4, 1.1, c_abdomen))
        self.abdomen.setPos(0.0, -2.0, -0.1)

        # 7. Wings (Left & Right) with hinge pivots
        self.wing_pivot_l = self.root.attachNewNode("WingPivotL")
        self.wing_pivot_l.setPos(-0.6, -0.2, 0.6)
        self.wing_l = self.wing_pivot_l.attachNewNode(create_wing_geom(length=3.2, width=1.4))
        self.wing_l.setHpr(120, -10, 0)
        self.wing_pivot_l.setTransparency(TransparencyAttrib.MAlpha)

        self.wing_pivot_r = self.root.attachNewNode("WingPivotR")
        self.wing_pivot_r.setPos(0.6, -0.2, 0.6)
        self.wing_r = self.wing_pivot_r.attachNewNode(create_wing_geom(length=3.2, width=1.4))
        self.wing_r.setHpr(-120, -10, 0)
        self.wing_pivot_r.setTransparency(TransparencyAttrib.MAlpha)

        # 8. Articulated 6 Legs (Front L/R, Mid L/R, Rear L/R)
        self.legs = []
        leg_configs = [
            ("FL", -0.7,  0.5, -25,  30, 0),
            ("FR",  0.7,  0.5,  25, -30, 1),
            ("ML", -0.7, -0.1, -25,   0, 1),
            ("MR",  0.7, -0.1,  25,   0, 0),
            ("RL", -0.7, -0.7, -25, -30, 0),
            ("RR",  0.7, -0.7,  25,  30, 1),
        ]
        for name, sx, sy, roll, yaw, tripod_phase in leg_configs:
            pivot = self.root.attachNewNode(f"LegPivot_{name}")
            pivot.setPos(sx, sy, -0.6)
            pivot.setHpr(yaw, 0, roll)
            leg_geom = pivot.attachNewNode(create_cube_geom(0.15, 0.15, 1.2, c_leg))
            leg_geom.setPos(0, 0, -0.5)
            self.legs.append((pivot, tripod_phase))

        self._wingbeat_phase = 0.0
        self._walking_phase = 0.0
        self.proboscis_extension = 0.0

    def set_proboscis_extension(self, extension: float):
        """Sets proboscis extension (0.0 = fully retracted, 1.0 = fully extended)."""
        self.proboscis_extension = float(max(0.0, min(1.0, extension)))
        # Retracted: P = -50.0 (tucked along ventral head/thorax); Extended: P = -5.0 (pointing downwards into food substrate)
        target_pitch = -50.0 + self.proboscis_extension * 45.0
        self.proboscis_pivot.setP(target_pitch)
        # Elongate stem downwards towards substrate
        scale_z = 1.0 + self.proboscis_extension * 0.9
        self.proboscis_stem.setScale(1.0, 1.0, scale_z)

    def animate(self, dt: float, flying: bool = True, speed: float = 0.0, grooming: bool = False):
        """Animates wingbeats during flight, tripod leg gaits during walking, and front-leg grooming."""
        if flying:
            self._wingbeat_phase += dt * 35.0
            angle = math.sin(self._wingbeat_phase) * 28.0
            self.wing_pivot_l.setR(angle)
            self.wing_pivot_r.setR(-angle)
            # Legs drawn up against body during flight
            for pivot, _ in self.legs:
                pivot.setP(0.0)
        else:
            # Wings folded back over abdomen at rest
            self.wing_pivot_l.setR(0.0)
            self.wing_pivot_r.setR(0.0)

            if grooming:
                # DNg12 front-leg grooming: rapid reciprocal sweeps of front tarsi over head
                self._walking_phase += dt * 25.0
                rub = math.sin(self._walking_phase) * 25.0
                self.legs[0][0].setP(35.0 + rub)
                self.legs[1][0].setP(35.0 - rub)
                for i in range(2, 6):
                    self.legs[i][0].setP(0.0)
            elif speed > 0.1:
                # Canonical Drosophila tripod walking gait: alternating sets of 3 legs
                self._walking_phase += dt * min(15.0, speed * 4.0)
                for pivot, phase in self.legs:
                    offset = 0.0 if phase == 0 else math.pi
                    swing = math.sin(self._walking_phase + offset) * 18.0
                    pivot.setP(swing)
            else:
                for pivot, _ in self.legs:
                    pivot.setP(0.0)
