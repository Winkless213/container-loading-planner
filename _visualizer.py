# -*- coding: utf-8 -*-
"""
装柜可视化：生成三视图 PNG
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import font_manager


def _setup_cjk_font():
    for fname in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
                  "Noto Sans CJK JP", "WenQuanYi Zen Hei", "PingFang SC"]:
        try:
            font_manager.findfont(fname, fallback_to_default=False)
            plt.rcParams["font.sans-serif"] = [fname] + plt.rcParams["font.sans-serif"]
            plt.rcParams["font.family"] = fname
            plt.rcParams["axes.unicode_minus"] = False
            return
        except Exception:
            continue
_setup_cjk_font()


def _draw3d_box(ax, x, y, z, dx, dy, dz, color, alpha=0.75):
    xx=[x,x+dx]; yy=[y,y+dy]; zz=[z,z+dz]
    faces = [
        [(xx[0],yy[0],zz[0]),(xx[1],yy[0],zz[0]),(xx[1],yy[1],zz[0]),(xx[0],yy[1],zz[0])],
        [(xx[0],yy[0],zz[1]),(xx[1],yy[0],zz[1]),(xx[1],yy[1],zz[1]),(xx[0],yy[1],zz[1])],
        [(xx[0],yy[0],zz[0]),(xx[1],yy[0],zz[0]),(xx[1],yy[0],zz[1]),(xx[0],yy[0],zz[1])],
        [(xx[0],yy[1],zz[0]),(xx[1],yy[1],zz[0]),(xx[1],yy[1],zz[1]),(xx[0],yy[1],zz[1])],
        [(xx[0],yy[0],zz[0]),(xx[0],yy[1],zz[0]),(xx[0],yy[1],zz[1]),(xx[0],yy[0],zz[1])],
        [(xx[1],yy[0],zz[0]),(xx[1],yy[1],zz[0]),(xx[1],yy[1],zz[1]),(xx[1],yy[0],zz[1])],
    ]
    ax.add_collection3d(Poly3DCollection(faces, alpha=alpha, facecolor=color,
                                          edgecolor="black", linewidth=0.6))


def render_loading_plan(placed, unfitted, spec, output_path, title=""):
    """生成单张三视图 PNG"""
    from collections import OrderedDict
    from matplotlib.patches import Patch

    L, W, H = spec["L"], spec["W"], spec["H"]
    cbm_cap = L * W * H / 1_000_000
    cbm_used = sum(p.length*p.width*p.height for p in placed) / 1_000_000
    w_total = sum(p.weight for p in placed)

    # 按首次出现顺序收集每个 SKU 的颜色 + 数量 (用于顶部图例)
    sku_info = OrderedDict()
    for p in placed:
        if p.sku_model not in sku_info:
            sku_info[p.sku_model] = {"color": p.color, "count": 0}
        sku_info[p.sku_model]["count"] += 1

    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.5, 1, 1],
                           height_ratios=[1, 1], hspace=0.3, wspace=0.3,
                           top=0.88)  # 顶部留空间给图例

    ax1 = fig.add_subplot(gs[:, 0], projection="3d")
    ax1.set_title("3D 装柜效果图", fontsize=13, fontweight="bold", pad=15)
    _draw3d_box(ax1, 0, 0, 0, L, W, H, "lightgray", alpha=0.03)
    for p in placed:
        _draw3d_box(ax1, p.x, p.y, p.z, p.length, p.width, p.height, p.color)
    ax1.set_xlim(0, L); ax1.set_ylim(0, W); ax1.set_zlim(0, H)
    ax1.set_xlabel("长 (cm)"); ax1.set_ylabel("宽 (cm)"); ax1.set_zlabel("高 (cm)")
    ax1.set_box_aspect([L, W, H]); ax1.view_init(elev=22, azim=-55)

    ax2 = fig.add_subplot(gs[0, 1:])
    ax2.set_title("俯视图（从上往下看）", fontsize=12, fontweight="bold")
    ax2.add_patch(Rectangle((0, 0), L, W, fill=False, edgecolor="black", linewidth=2))
    for p in placed:
        # 纯色色块, 不再写型号文字
        ax2.add_patch(Rectangle((p.x, p.y), p.length, p.width,
                                 facecolor=p.color, edgecolor="black",
                                 alpha=0.85, linewidth=0.6))
    ax2.set_xlim(-40, L+80); ax2.set_ylim(-30, W+30); ax2.set_aspect("equal")
    ax2.set_xlabel("长 (cm)"); ax2.set_ylabel("宽 (cm)"); ax2.grid(True, alpha=0.3)
    ax2.annotate("柜门", xy=(L, W/2), xytext=(L+50, W/2), fontsize=10,
                 ha="left", va="center", color="red",
                 arrowprops=dict(arrowstyle="->", color="red", lw=1.5))
    ax2.annotate("柜尾", xy=(0, W/2), xytext=(-30, W/2), fontsize=10,
                 ha="right", va="center", color="gray")

    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_title("侧视图（从侧面看）", fontsize=12, fontweight="bold")
    ax3.add_patch(Rectangle((0, 0), L, H, fill=False, edgecolor="black", linewidth=2))
    for p in placed:
        ax3.add_patch(Rectangle((p.x, p.z), p.length, p.height,
                                 facecolor=p.color, edgecolor="black",
                                 alpha=0.85, linewidth=0.5))
    ax3.set_xlim(-30, L+30); ax3.set_ylim(-30, H+30); ax3.set_aspect("equal")
    ax3.set_xlabel("长 (cm)"); ax3.set_ylabel("高 (cm)"); ax3.grid(True, alpha=0.3)

    ax4 = fig.add_subplot(gs[1, 2])
    ax4.axis("off"); ax4.set_title("装柜统计", fontsize=12, fontweight="bold")
    rows = [
        ("柜型", spec.get("name", "")),
        ("内部尺寸", f"{L/100:.2f}×{W/100:.2f}×{H/100:.2f} m"),
        ("理论容积", f"{cbm_cap:.2f} m³"),
        ("限重", f"{spec['max_kg']:,} kg"),
        ("", ""),
        ("已装箱数", f"{len(placed)} 箱"),
        ("未装下", f"{sum(c for _,c in unfitted)} 箱" if unfitted else "0 箱"),
        ("占用体积", f"{cbm_used:.2f} m³"),
        ("总重量", f"{w_total:,.0f} kg"),
        ("", ""),
        ("体积利用率", f"{cbm_used/cbm_cap*100:.1f} %"),
        ("重量利用率", f"{w_total/spec['max_kg']*100:.1f} %"),
    ]
    y = 0.92
    for label, value in rows:
        if label:
            ax4.text(0.03, y, label, transform=ax4.transAxes, fontsize=11,
                     verticalalignment="top", fontweight="bold")
            ax4.text(0.48, y, value, transform=ax4.transAxes, fontsize=11,
                     verticalalignment="top")
        y -= 0.075
    ax4.add_patch(Rectangle((0, 0), 1, 1, transform=ax4.transAxes,
                             fill=False, edgecolor="gray", linewidth=1))

    # 顶部图例: 色块 + 型号 + 数量 (替代每箱上写文字)
    if sku_info:
        handles = [Patch(facecolor=info["color"], edgecolor="black", linewidth=0.6,
                         label=f"{sku}  ×{info['count']}箱")
                   for sku, info in sku_info.items()]
        n = len(handles)
        ncol = min(n, 6 if n <= 12 else 7)
        fig.legend(handles=handles, loc="upper center",
                   bbox_to_anchor=(0.5, 0.95),
                   ncol=ncol, fontsize=10, frameon=True,
                   handlelength=1.8, handleheight=1.2,
                   columnspacing=1.5, labelspacing=0.5)

    if title:
        fig.suptitle(title, fontsize=15, fontweight="bold", y=0.99)
    plt.savefig(output_path, dpi=110, bbox_inches="tight")
    plt.close()
