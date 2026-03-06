import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { NextRequest, NextResponse } from "next/server";

// GET /api/plugins - List plugins with search/filter
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const search = searchParams.get("search");
    const categoryId = searchParams.get("categoryId");
    const featured = searchParams.get("featured");

    const where: Record<string, unknown> = {};

    if (search) {
      where.OR = [
        { name: { contains: search } },
        { description: { contains: search } },
        { author: { contains: search } },
        { tags: { contains: search } },
      ];
    }

    if (categoryId) {
      where.categoryId = categoryId;
    }

    if (featured === "true") {
      where.featured = true;
    }

    const plugins = await prisma.plugin.findMany({
      where,
      include: {
        category: true,
        _count: { select: { favorites: true } },
      },
      orderBy: { createdAt: "desc" },
    });

    return NextResponse.json(plugins);
  } catch (error) {
    console.error("Failed to fetch plugins:", error);
    return NextResponse.json(
      { error: "Failed to fetch plugins" },
      { status: 500 }
    );
  }
}

// POST /api/plugins - Create plugin (admin only)
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session || session.user?.role !== "ADMIN") {
      return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
    }

    const body = await request.json();
    const { name, description, author, imageUrl, figmaUrl, categoryId, tags, featured } = body;

    if (!name || !description || !author || !categoryId) {
      return NextResponse.json(
        { error: "Missing required fields: name, description, author, categoryId" },
        { status: 400 }
      );
    }

    const plugin = await prisma.plugin.create({
      data: {
        name,
        description,
        author,
        imageUrl: imageUrl || null,
        figmaUrl: figmaUrl || null,
        categoryId,
        tags: tags || "",
        featured: featured || false,
      },
      include: { category: true },
    });

    return NextResponse.json(plugin, { status: 201 });
  } catch (error) {
    console.error("Failed to create plugin:", error);
    return NextResponse.json(
      { error: "Failed to create plugin" },
      { status: 500 }
    );
  }
}
