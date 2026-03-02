package com.patas_sem_lar.mvp.dto;

public record RegisterDTO(String email, String password_hash, String name, String slug, String phone, String addressLine1, String city, String postalCode ) {
}
