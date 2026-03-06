import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";

const prisma = new PrismaClient();

async function main() {
  console.log("🌱 Seeding database...");

  // Create admin user
  const adminPassword = await bcrypt.hash("admin123", 12);
  const admin = await prisma.user.upsert({
    where: { email: "admin@pluginhub.dev" },
    update: {},
    create: {
      email: "admin@pluginhub.dev",
      password: adminPassword,
      name: "Admin",
      role: "ADMIN",
    },
  });
  console.log("✅ Admin user created:", admin.email);

  // Create test user
  const userPassword = await bcrypt.hash("user1234", 12);
  const user = await prisma.user.upsert({
    where: { email: "user@pluginhub.dev" },
    update: {},
    create: {
      email: "user@pluginhub.dev",
      password: userPassword,
      name: "Test User",
      role: "USER",
    },
  });
  console.log("✅ Test user created:", user.email);

  // Create categories
  const categories = await Promise.all([
    prisma.category.upsert({
      where: { slug: "design-tools" },
      update: {},
      create: {
        name: "Design Tools",
        slug: "design-tools",
        description: "Essential tools for design workflow",
        icon: "🎨",
      },
    }),
    prisma.category.upsert({
      where: { slug: "prototyping" },
      update: {},
      create: {
        name: "Prototyping",
        slug: "prototyping",
        description: "Interactive prototypes and animations",
        icon: "🚀",
      },
    }),
    prisma.category.upsert({
      where: { slug: "developer-handoff" },
      update: {},
      create: {
        name: "Developer Handoff",
        slug: "developer-handoff",
        description: "Bridge between design and development",
        icon: "🔧",
      },
    }),
    prisma.category.upsert({
      where: { slug: "content" },
      update: {},
      create: {
        name: "Content",
        slug: "content",
        description: "Content generation and management",
        icon: "📝",
      },
    }),
    prisma.category.upsert({
      where: { slug: "accessibility" },
      update: {},
      create: {
        name: "Accessibility",
        slug: "accessibility",
        description: "A11y testing and improvements",
        icon: "♿",
      },
    }),
    prisma.category.upsert({
      where: { slug: "collaboration" },
      update: {},
      create: {
        name: "Collaboration",
        slug: "collaboration",
        description: "Team collaboration and feedback",
        icon: "👥",
      },
    }),
    prisma.category.upsert({
      where: { slug: "icons-illustrations" },
      update: {},
      create: {
        name: "Icons & Illustrations",
        slug: "icons-illustrations",
        description: "Icon libraries and illustration resources",
        icon: "✨",
      },
    }),
    prisma.category.upsert({
      where: { slug: "color-typography" },
      update: {},
      create: {
        name: "Color & Typography",
        slug: "color-typography",
        description: "Color palettes, fonts, and typography tools",
        icon: "🎯",
      },
    }),
  ]);
  console.log(`✅ ${categories.length} categories created`);

  // Create plugins
  const pluginsData = [
    {
      name: "Auto Layout Helper",
      description:
        "Automatically applies Auto Layout to selected frames with smart padding and spacing detection. Saves hours of manual layout work.",
      author: "Figma Community",
      categorySlug: "design-tools",
      tags: "auto-layout,spacing,frames,productivity",
      featured: true,
      figmaUrl: "https://www.figma.com/community/plugin/auto-layout-helper",
    },
    {
      name: "Content Reel",
      description:
        "Pull text strings, images, and icons into your designs. Generate realistic content for mockups instantly.",
      author: "Microsoft Design",
      categorySlug: "content",
      tags: "content,images,text,mockup",
      featured: true,
      figmaUrl: "https://www.figma.com/community/plugin/content-reel",
    },
    {
      name: "Contrast Checker",
      description:
        "Check the contrast ratio between two colors and ensure WCAG compliance. Essential for accessible design.",
      author: "A11y Tools",
      categorySlug: "accessibility",
      tags: "contrast,wcag,a11y,colors",
      featured: true,
      figmaUrl: "https://www.figma.com/community/plugin/contrast-checker",
    },
    {
      name: "Figmotion",
      description:
        "Create animations directly in Figma. Export to CSS, Lottie, or GIF. No coding required.",
      author: "Figmotion Team",
      categorySlug: "prototyping",
      tags: "animation,motion,lottie,css",
      featured: true,
      figmaUrl: "https://www.figma.com/community/plugin/figmotion",
    },
    {
      name: "Locofy",
      description:
        "Convert Figma designs to production-ready code. Supports React, Next.js, Vue, and HTML/CSS.",
      author: "Locofy.ai",
      categorySlug: "developer-handoff",
      tags: "code,react,nextjs,html,css,export",
      featured: true,
      figmaUrl: "https://www.figma.com/community/plugin/locofy",
    },
    {
      name: "Iconify",
      description:
        "Access 150,000+ icons from 100+ icon sets. Material, FontAwesome, Heroicons, and more.",
      author: "Iconify",
      categorySlug: "icons-illustrations",
      tags: "icons,material,fontawesome,heroicons",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/iconify",
    },
    {
      name: "Color Palettes",
      description:
        "Generate beautiful color palettes from images, color theory, or trending palettes. Export to CSS variables.",
      author: "Palette Studio",
      categorySlug: "color-typography",
      tags: "color,palette,css,variables,themes",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/color-palettes",
    },
    {
      name: "Design Lint",
      description:
        "Find and fix inconsistencies in your designs. Check spacing, colors, typography, and component usage.",
      author: "Design Systems Co",
      categorySlug: "design-tools",
      tags: "lint,consistency,design-system,qa",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/design-lint",
    },
    {
      name: "FigJam Widgets",
      description:
        "A collection of useful widgets for FigJam. Voting, timers, sticky templates, and retrospective boards.",
      author: "Collaboration Lab",
      categorySlug: "collaboration",
      tags: "figjam,widgets,voting,retrospective",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/figjam-widgets",
    },
    {
      name: "Breakpoints",
      description:
        "Preview your designs at different breakpoints. Mobile, tablet, desktop. Responsive design made easy.",
      author: "Responsive Co",
      categorySlug: "prototyping",
      tags: "responsive,breakpoints,mobile,tablet",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/breakpoints",
    },
    {
      name: "Token Studio",
      description:
        "Manage design tokens in Figma. Sync with GitHub, define variables, and export to any platform.",
      author: "Tokens Studio",
      categorySlug: "developer-handoff",
      tags: "tokens,variables,github,sync,design-system",
      featured: true,
      figmaUrl: "https://www.figma.com/community/plugin/token-studio",
    },
    {
      name: "Stark",
      description:
        "Complete accessibility toolkit. Vision simulation, contrast checking, focus order, and alt text suggestions.",
      author: "Stark Lab Inc",
      categorySlug: "accessibility",
      tags: "a11y,vision,contrast,focus,alt-text",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/stark",
    },
    {
      name: "Unsplash",
      description:
        "Insert beautiful, free photos from Unsplash directly into your Figma designs.",
      author: "Unsplash",
      categorySlug: "content",
      tags: "photos,images,stock,free",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/unsplash",
    },
    {
      name: "Font Explorer",
      description:
        "Browse and preview Google Fonts directly in Figma. Compare fonts side by side and apply with one click.",
      author: "Type Foundry",
      categorySlug: "color-typography",
      tags: "fonts,google-fonts,typography,preview",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/font-explorer",
    },
    {
      name: "Blush Illustrations",
      description:
        "Create and customize beautiful illustrations. Mix and match styles, poses, and colors.",
      author: "Blush Design",
      categorySlug: "icons-illustrations",
      tags: "illustrations,characters,customizable,svg",
      featured: false,
      figmaUrl: "https://www.figma.com/community/plugin/blush",
    },
  ];

  for (const pluginData of pluginsData) {
    const category = categories.find((c) => c.slug === pluginData.categorySlug);
    if (!category) continue;

    await prisma.plugin.create({
      data: {
        name: pluginData.name,
        description: pluginData.description,
        author: pluginData.author,
        categoryId: category.id,
        tags: pluginData.tags,
        featured: pluginData.featured,
        figmaUrl: pluginData.figmaUrl,
        imageUrl: null,
      },
    });
  }
  console.log(`✅ ${pluginsData.length} plugins created`);

  // Create some favorites for the test user
  const allPlugins = await prisma.plugin.findMany({ take: 5 });
  for (const plugin of allPlugins) {
    await prisma.favorite.create({
      data: {
        userId: user.id,
        pluginId: plugin.id,
      },
    });
  }
  console.log("✅ Sample favorites created");

  console.log("\n🎉 Seed complete!");
  console.log("───────────────────────────");
  console.log("Admin: admin@pluginhub.dev / admin123");
  console.log("User:  user@pluginhub.dev  / user1234");
  console.log("───────────────────────────");
}

main()
  .catch((e) => {
    console.error("❌ Seed failed:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
