package com.patas_sem_lar.mvp.services;


import com.patas_sem_lar.mvp.entities.Animal;
import com.patas_sem_lar.mvp.repositories.AnimalRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AnimalService {

    private final AnimalRepository animalRepository;

    public List<Animal> getAllAnimals() {
        return animalRepository.findAll();
    }

    public List<Animal> getAvailableAnimals() {
        return animalRepository.findAvailableAnimals();
    }

    public Animal getAnimalById(Long id) {
        return animalRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Animal not found with id: " + id));
    }

    @Transactional
    public Animal createAnimal(Animal animal) {
        return animalRepository.save(animal);
    }

    @Transactional
    public Animal updateAnimal(Long id, Animal updatedAnimal) {
        Animal existing = getAnimalById(id);
        existing.setName(updatedAnimal.getName());
        // Podemos incluir atualizacao de qualquer dos outros campos
        return animalRepository.save(existing);
    }

    @Transactional
    public void deleteAnimal(Long id) {
        animalRepository.deleteById(id);
    }
}
