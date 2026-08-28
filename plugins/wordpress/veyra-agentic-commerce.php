<?php
/**
 * Plugin Name: Veyra — Agentic Commerce for WooCommerce
 * Plugin URI: https://veyra.dev
 * Description: One-click OpenAI Instant Checkout + Google AP2 support for WooCommerce. Free tier proxies to Veyra hosted ACP endpoint.
 * Version: 0.1.0
 * Author: Veyra
 * Author URI: https://veyra.dev
 * License: GPL v2 or later
 * Requires PHP: 7.4
 * WC requires at least: 7.0
 * WC tested up to: 9.3
 */

if (!defined('ABSPATH')) exit;

define('VEYRA_ACP_ENDPOINT', 'https://api.veyra.dev');
define('VEYRA_ACP_VERSION', '0.1.0');

add_action('rest_api_init', function () {
    register_rest_route('veyra/v1', '/checkout_sessions', [
        'methods'  => 'POST',
        'callback' => 'veyra_proxy_create',
        'permission_callback' => '__return_true',
    ]);
    register_rest_route('veyra/v1', '/checkout_sessions/(?P<id>[a-zA-Z0-9_-]+)', [
        'methods'  => ['GET', 'POST'],
        'callback' => 'veyra_proxy_session',
        'permission_callback' => '__return_true',
    ]);
    register_rest_route('veyra/v1', '/checkout_sessions/(?P<id>[a-zA-Z0-9_-]+)/complete', [
        'methods'  => 'POST',
        'callback' => 'veyra_proxy_complete',
        'permission_callback' => '__return_true',
    ]);
    register_rest_route('veyra/v1', '/checkout_sessions/(?P<id>[a-zA-Z0-9_-]+)/cancel', [
        'methods'  => 'POST',
        'callback' => 'veyra_proxy_cancel',
        'permission_callback' => '__return_true',
    ]);
});

function veyra_proxy_request($path, $body, $headers) {
    $api_key = get_option('veyra_api_key', '');
    if (!$api_key) {
        return new WP_Error('no_api_key', 'Veyra API key not configured. Get one at https://veyra.dev/signup', ['status' => 401]);
    }
    $forwarded = [
        'Authorization' => 'Bearer ' . $api_key,
        'Content-Type'  => 'application/json',
        'API-Version'   => '2025-09-12',
    ];
    foreach (['Signature', 'Timestamp', 'Idempotency-Key', 'Request-Id'] as $h) {
        if (isset($headers[strtolower($h)])) $forwarded[$h] = $headers[strtolower($h)][0];
    }
    $resp = wp_remote_post(VEYRA_ACP_ENDPOINT . $path, [
        'headers' => $forwarded,
        'body'    => wp_json_encode($body),
        'timeout' => 20,
    ]);
    if (is_wp_error($resp)) return $resp;
    return json_decode(wp_remote_retrieve_body($resp), true);
}

function veyra_proxy_create($req)   { return veyra_proxy_request('/checkout_sessions', $req->get_json_params(), $req->get_headers()); }
function veyra_proxy_session($req)  { return veyra_proxy_request('/checkout_sessions/' . $req['id'], $req->get_json_params(), $req->get_headers()); }
function veyra_proxy_complete($req) { return veyra_proxy_request('/checkout_sessions/' . $req['id'] . '/complete', $req->get_json_params(), $req->get_headers()); }
function veyra_proxy_cancel($req)   { return veyra_proxy_request('/checkout_sessions/' . $req['id'] . '/cancel', $req->get_json_params(), $req->get_headers()); }

add_action('admin_menu', function () {
    add_options_page('Veyra Agentic Commerce', 'Veyra ACP', 'manage_options', 'veyra-acp', 'veyra_settings_page');
});

function veyra_settings_page() {
    if (!current_user_can('manage_options')) return;
    if (isset($_POST['veyra_api_key'])) {
        update_option('veyra_api_key', sanitize_text_field($_POST['veyra_api_key']));
        echo '<div class="notice notice-success"><p>Saved.</p></div>';
    }
    $key = esc_attr(get_option('veyra_api_key', ''));
    echo '<div class="wrap"><h1>Veyra — Agentic Commerce</h1>';
    echo '<p>Get your Veyra API key at <a href="https://veyra.dev/signup" target="_blank">veyra.dev/signup</a>.</p>';
    echo '<form method="post"><table class="form-table"><tr><th>API Key</th><td><input type="text" name="veyra_api_key" value="' . $key . '" style="width:400px" /></td></tr></table>';
    submit_button('Save');
    echo '</form></div>';
}
