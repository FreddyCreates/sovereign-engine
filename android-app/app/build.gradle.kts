import java.util.Properties
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.roborazzi)
}

// Secrets and per-machine settings come from android-app/local.properties
// (git-ignored) or from environment variables. Nothing sensitive is in source.
val localProps = Properties().apply {
    val f = rootProject.file("local.properties")
    if (f.isFile) f.inputStream().use { load(it) }
}

fun setting(name: String, default: String = ""): String =
    localProps.getProperty(name) ?: System.getenv(name) ?: default

android {
    namespace = "com.sovereignengine.books"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.sovereignengine.books"
        minSdk = 26
        targetSdk = 36
        versionCode = setting("VERSION_CODE", "1").toInt()
        versionName = setting("VERSION_NAME", "1.0.0")

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // Public RevenueCat SDK key for the Google Play app (goog_...).
        buildConfigField("String", "REVENUECAT_GOOGLE_API_KEY", "\"${setting("REVENUECAT_GOOGLE_API_KEY")}\"")
        // Entitlement identifier configured in the RevenueCat dashboard.
        buildConfigField("String", "REVENUECAT_ENTITLEMENT_ID", "\"${setting("REVENUECAT_ENTITLEMENT_ID", "pro_access")}\"")
        // Base URL of the Sovereign Books API (sovereign_dashboard_server.py).
        buildConfigField("String", "BOOKS_API_BASE_URL", "\"${setting("BOOKS_API_BASE_URL", "http://10.0.2.2:8090")}\"")
    }

    signingConfigs {
        create("release") {
            val storePath = setting("KEYSTORE_PATH")
            if (storePath.isNotEmpty()) {
                storeFile = file(storePath)
                storePassword = setting("KEYSTORE_PASSWORD")
                keyAlias = setting("KEY_ALIAS")
                keyPassword = setting("KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            // Only sign when a keystore is configured; unsigned bundles still build for CI.
            if (setting("KEYSTORE_PATH").isNotEmpty()) {
                signingConfig = signingConfigs.getByName("release")
            }
        }
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }


    buildFeatures {
        compose = true
        buildConfig = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }

    testOptions {
        unitTests {
            isIncludeAndroidResources = true
            isReturnDefaultValues = true
        }
    }

    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}

kotlin {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_17)
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.google.material)

    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.material.icons)
    debugImplementation(libs.androidx.compose.ui.tooling)

    // RevenueCat: Google Play Billing plus Paywalls and Customer Center UI.
    implementation(libs.revenuecat.purchases)
    implementation(libs.revenuecat.purchases.ui)

    testImplementation(libs.junit)
    // Screenshot rendering on the JVM (no emulator): Robolectric + Roborazzi.
    testImplementation(libs.androidx.test.ext.junit)
    testImplementation(libs.androidx.compose.ui.test.junit4)
    testImplementation(libs.robolectric)
    testImplementation(libs.roborazzi)
    testImplementation(libs.roborazzi.compose)
    testImplementation(libs.roborazzi.junit.rule)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
}

// Screenshots land in docs/play-store/screenshots so the store listing and the
// walkthrough use real renders of the app.
roborazzi {
    outputDir.set(rootProject.file("../docs/play-store/screenshots"))
}
