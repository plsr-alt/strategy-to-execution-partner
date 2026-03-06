import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { NextRequest, NextResponse } from "next/server";

// GET /api/plugins/[id] - Get single plugin
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    const plugin = await prisma.plugin.findUnique({
      where: { id },
      include: {
        category: true,
        _count: { select: { favorites: true } },
      },
    });

    if (!plugin) {
      return NextResponse.json({ error: "Plugin not found" }, { status: 404 });
    }

    return NextResponse.json(plugin);
  } catch (error) {
    console.error("Failed to fetch plugin:", error);
    return NextResponse.json(
      { error: "Failed to fetch plugin" },
      { status: 500 }
    );
  }
}

// PUT /api/plugins/[id] - Update plugin (admin only)
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getServerSession(authOptions);

    if (!session || session.user?.role !== "ADMIN") {
      return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
    }

    const { id } = await params;
    const body = await request.json();
    const { name, description, author, imageUrl, figmaUrl, categoryId, tags, featured } = body;

    const existing = await prisma.plugin.findUnique({ where: { id } });
    if (!existing) {
      return NextResponse.json({ error: "Plugin not found" }, { status: 404 });
    }

    const plugin = await prisma.plugin.update({
      where: { id },
      data: {
        ...(name !== undefined && { name }),
        ...(description !== undefined && { description }),
        ...(author !== undefined && { author }),
        ...(imageUrl !== undefined && { imageUrl }),
        ...(figmaUrl !== undefined && { figmaUrl }),
        ...(categoryId !== undefined && { categoryId }),
        ...(tags !== undefined && { tags }),
        ...(featured !== undefined && { featured }),
      },
      include: { category: true },
    });

    return NextResponse.json(plugin);
  } catch (error) {
    console.error("Failed to update plugin:", error);
    return NextResponse.json(
      { error: "Failed to update plugin" },
      { status: 500 }
    );
  }
}

// DELETE /api/plugins/[id] - Delete plugin (admin only)
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getServerSession(authOptions);

    if (!session || session.user?.role !== "ADMIN") {
      return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
    }

    const { id } = await params;

    const existing = await prisma.plugin.findUnique({ where: { id } });
    if (!existing) {
      return NextResponse.json({ error: "Plugin not found" }, { status: 404 });
    }

    await prisma.plugin.delete({ where: { id } });

    return NextResponse.json({ message: "Plugin deleted" });
  } catch (error) {
    console.error("Failed to delete plugin:", error);
    return NextResponse.json(
      { error: "Failed to delete plugin" },
      { status: 500 }
    );
  }
}
