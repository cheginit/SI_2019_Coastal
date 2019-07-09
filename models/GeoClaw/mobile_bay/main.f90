program main

    use tide_module

    implicit none
    integer :: i, wl_size
    real(kind=8), dimension (:), allocatable :: time_input, water_level
    real(kind=8) :: time, y

    call setup_tide(time_input, water_level, wl_size)

    time = (time_input(1) + time_input(2)) * 0.5

    do i = 2, wl_size
        if ((time > time_input(i-1)) .and. (time < time_input(i))) then
            call parabola_val2(wl_size, time_input, water_level, i, time, y)
            !call linear_val2(y, time, &
            !                & water_level(i-1), water_level(i), &
            !                & time_input(i-1), time_input(i))
            exit
        end if
    end do

    write(*,*) time, y, water_level(1), water_level(2)

    call setup_tide(time_input, water_level, wl_size)

    time = (time_input(3) + time_input(4)) * 0.5

    do i = 2, wl_size
        if ((time > time_input(i-1)) .and. (time < time_input(i))) then
            call parabola_val2(wl_size, time_input, water_level, i, time, y)
            !call linear_val2(y, time, &
            !                & water_level(i-1), water_level(i), &
            !                & time_input(i-1), time_input(i))
            exit
        end if
    end do

    write(*,*) time, y, water_level(3), water_level(4)

    deallocate(time_input)
    deallocate(water_level)

end program main
