import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { NextRequest, NextResponse } from "next/server";

// GET /api/favorites - Get current user's favorites
export async function GET() {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const favorites = await prisma.favorite.findMany({
      where: { userId: session.user.id },
      include: {
        plugin: {
          include: {
            category: true,
            _count: { select: { favorites: true } },
          },
        },
      },
      orderBy: { createdAt: "desc" },
    });

    return NextResponse.json(favorites);
  } catch (error) {
    console.error("Failed to fetch favorites:", error);
    return NextResponse.json(
      { error: "Failed to fetch favorites" },
      { status: 500 }
    );
  }
}

// POST /api/favorites - Toggle favorite (add if not exists, remove if exists)
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { pluginId } = body;

    if (!pluginId) {
      return NextResponse.json(
        { error: "Missing required field: pluginId" },
        { status: 400 }
      );
    }

    const plugin = await prisma.plugin.findUnique({ where: { id: pluginId } });
    if (!plugin) {
      return NextResponse.json(
        { error: "Plugin not found" },
        { status: 404 }
      );
    }

    const existing = await prisma.favorite.findUnique({
      where: {
        userId_pluginId: {
          userId: session.user.id,
          pluginId,
        },
      },
    });

    if (existing) {
      await prisma.favorite.delete({ where: { id: existing.id } });
      return NextResponse.json({ favorited: false, message: "Favorite removed" });
    } else {
      const favorite = await prisma.favorite.create({
        data: {
          userId: session.user.id,
          pluginId,
        },
      });
      return NextResponse.json({ favorited: true, message: "Favorite added", favorite }, { status: 201 });
    }
  } catch (error) {
    console.error("Failed to toggle favorite:", error);
    return NextResponse.json(
      { error: "Failed to toggle favorite" },
      { status: 500 }
    );
  }
}
