import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET() {
  try {
    const session = await getServerSession(authOptions);
    if (!session || (session.user as { role?: string })?.role !== "ADMIN") {
      return NextResponse.json({ error: "Unauthorized" }, { status: 403 });
    }

    const [pluginCount, categoryCount, userCount, favoriteCount, recentPlugins] =
      await Promise.all([
        prisma.plugin.count(),
        prisma.category.count(),
        prisma.user.count(),
        prisma.favorite.count(),
        prisma.plugin.findMany({
          take: 5,
          orderBy: { createdAt: "desc" },
          include: { category: { select: { name: true } } },
        }),
      ]);

    return NextResponse.json({
      pluginCount,
      categoryCount,
      userCount,
      favoriteCount,
      recentPlugins,
    });
  } catch (error) {
    console.error("Stats error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
