# Stack Detection

When repository access is available, infer the UI stack from project files before giving stack-specific implementation advice.

## High-confidence signals

- Next.js: `next` dependency in `package.json`, `next.config.*`, or `app/`/`pages/` with Next conventions.
- React: `react` dependency without a stronger framework signal.
- Vue: `vue` dependency or `.vue` single-file components.
- Nuxt: `nuxt` dependency or `nuxt.config.*`.
- Svelte/SvelteKit: `svelte` or `@sveltejs/kit` dependencies.
- Astro: `astro` dependency or `astro.config.*`.
- Angular: `@angular/core` or `angular.json`.
- Flutter: `pubspec.yaml` with Flutter SDK.
- SwiftUI: Swift sources importing SwiftUI, `Package.swift`, or Xcode project metadata.
- React Native: `react-native` dependency and RN project structure.
- Jetpack Compose: Gradle dependencies for Compose and Kotlin UI sources.
- Laravel: `composer.json` with `laravel/framework`.
- Three.js: `three` dependency and scene/rendering code.
- WPF/WinUI/UWP/Avalonia/Uno/JavaFX: project files and framework-specific package/import signals.

## Rules

- Prefer the strongest specific framework signal over a generic library signal.
- Do not assume Tailwind just because utility-like class names appear; confirm dependency/configuration.
- If multiple UI stacks coexist, scope guidance to the relevant app/package.
- If no stack is detectable and implementation details matter, ask once or use stack-neutral HTML/CSS guidance.
